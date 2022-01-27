
from functools import lru_cache
import inspect

from sqlalchemy.orm import Query
from sqlalchemy.orm import ColumnProperty
from sqlalchemy.orm import aliased
from sqlalchemy.orm.attributes import QueryableAttribute

from http.client import BAD_REQUEST
from http.client import NOT_FOUND

def session_query(session, model):
    """Returns a SQLAlchemy query object for the specified `model`.
    If `model` has a ``query`` attribute already, ``model.query`` will be
    returned. If the ``query`` attribute is callable ``model.query()`` will be
    returned instead.
    If `model` has no such attribute, a query based on `session` will be
    created and returned.
    """
    if hasattr(model, 'query'):
        if callable(model.query):
            query = model.query()
        else:
            query = model.query
        if isinstance(query, Query):
            if query.session is None:
                query = query.with_session(session)
            return query
    return session.query(model)

@lru_cache()
def primary_key_names(model):
    """Returns all the primary keys for a model."""
    return [key for key, field in inspect.getmembers(model)
            if isinstance(field, QueryableAttribute)
            and hasattr(field, 'property')
            and isinstance(field.property, ColumnProperty)
            and field.property.columns[0].primary_key]


class Error(Exception):
    http_code = 500

    def __init__(self, cause=None, details=None):
        self.cause = cause
        self.details = details


class BadRequest(Error):
    http_code = BAD_REQUEST


class NotFound(Error):
    http_code = NOT_FOUND

#: The mapping from operator name (as accepted by the search method) to a
#: function which returns the SQLAlchemy expression corresponding to that
#: operator.
#:
#: Each of these functions accepts either one, two, or three arguments. The
#: first argument is the field object on which to apply the operator. The
#: second argument, where it exists, is either the second argument to the
#: operator or a dictionary as described below. The third argument, where it
#: exists, is the name of the field.
#:
#: For functions that accept three arguments, the second argument may be a
#: dictionary containing ``'name'``, ``'op'``, and ``'val'`` mappings so that
#: :func:`create_operation` may be applied recursively. For more information
#: and examples, see :ref:`search`.
#:
#: Some operations have multiple names. For example, the equality operation can
#: be described by the strings ``'=='``, ``'eq'``, ``'equals'``, etc.
OPERATORS = {
    # Operators which accept a single argument.
    'is_null': lambda f: f.is_(None),
    'is_not_null': lambda f: f.isnot(None),
    # Operators which accept two arguments.
    '==': lambda f, a: f == a,
    'eq': lambda f, a: f == a,
    '!=': lambda f, a: f != a,
    'ne': lambda f, a: f != a,
    '>': lambda f, a: f > a,
    'gt': lambda f, a: f > a,
    '<': lambda f, a: f < a,
    'lt': lambda f, a: f < a,
    '>=': lambda f, a: f >= a,
    'ge': lambda f, a: f >= a,
    '<=': lambda f, a: f <= a,
    'le': lambda f, a: f <= a,
    'ilike': lambda f, a: f.ilike(a),
    'like': lambda f, a: f.like(a),
    'not_like': lambda f, a: ~f.like(a),
    'in': lambda f, a: f.in_(a),
    'not_in': lambda f, a: ~f.in_(a),
}

class UnknownField(Exception):
    """Raised when the user attempts to reference a field that does not
    exist on a model in a search.
    """

    def __init__(self, field):
        #: The name of the unknown attribute.
        self.field = field


class ComparisonToNull(Exception):
    """Raised when a client attempts to use a filter object that compares a
    resource's attribute to ``NULL`` using the ``==`` operator instead of using
    ``is_null``.
    """
    pass


class Filter(object):
    def __init__(self, fieldname, operator, argument=None, otherfield=None):
        self.fieldname = fieldname
        self.operator = operator
        self.argument = argument
        self.otherfield = otherfield
    
    @staticmethod
    def from_dictionary(model, dictionary):
        fieldname = dictionary.get('name')
        if not hasattr(model, fieldname):
            raise UnknownField(fieldname)
        operator = dictionary.get('op')
        otherfield = dictionary.get('field')
        argument = dictionary.get('val')
        # Need to deal with the special case of converting dates.
        # argument = string_to_datetime(model, fieldname, argument)
        return Filter(fieldname, operator, argument, otherfield)


def create_filter(model, filt):
    """Returns the operation on `model` specified by the provided filter.
    `filt` is an instance of the :class:`Filter` class.
    Raises one of :exc:`AttributeError`, :exc:`KeyError`, or
    :exc:`TypeError` if there is a problem creating the query. See the
    documentation for :func:`create_operation` for more information.
    """
    fname = filt.fieldname
    val = filt.argument
    return create_operation(model, fname, filt.operator, val)
    # return and_(create_filter(model, f) for f in filt)


def create_operation(model, fieldname, operator, argument):
    """Translates an operation described as a string to a valid SQLAlchemy
    query parameter using a field of the specified model.
    More specifically, this translates the string representation of an
    operation, for example ``'gt'``, to an expression corresponding to a
    SQLAlchemy expression, ``field > argument``. The recognized operators
    are given by the keys of :data:`OPERATORS`. For more information on
    recognized search operators, see :ref:`search`.
    `model` is an instance of a SQLAlchemy declarative model being
    searched.
    `fieldname` is the name of the field of `model` to which the operation
    will be applied as part of the search.
    `operation` is a string representating the operation which will be
     executed between the field and the argument received. For example,
     ``'gt'``, ``'lt'``, ``'like'``, ``'in'`` etc.
    `argument` is the argument to which to apply the `operator`.
    This function raises the following errors:
    * :exc:`KeyError` if the `operator` is unknown (that is, not in
      :data:`OPERATORS`)
    * :exc:`TypeError` if an incorrect number of arguments are provided for
      the operation (for example, if `operation` is `'=='` but no
      `argument` is provided)
    * :exc:`AttributeError` if no column with name `fieldname` or
      `relation` exists on `model`
    """
    # raises KeyError if operator not in OPERATORS
    opfunc = OPERATORS[operator]
    numargs = len(inspect.getfullargspec(opfunc).args)
    # raises AttributeError if `fieldname` does not exist
    field = getattr(model, fieldname)
    # each of these will raise a TypeError if the wrong number of argments
    # is supplied to `opfunc`.
    if numargs == 1:
        return opfunc(field)
    if argument is None:
        msg = ('To compare a value to NULL, use the is_null/is_not_null operators.')
        raise ComparisonToNull(msg)
    if numargs == 2:
        return opfunc(field, argument)
    return opfunc(field, argument, fieldname)


def search(session, model, filters=None):
    """Returns a SQLAlchemy query instance with the specified parameters.
    Each instance in the returned query meet the requirements specified by
    ``filters`` and ``sort``.
    This function returns a single instance of the model matching the search
    parameters if ``search_params['single']`` is ``True``, or a list of all
    such instances otherwise. If ``search_params['single']`` is ``True``, then
    this method will raise :exc:`sqlalchemy.orm.exc.NoResultFound` if no
    results are found and :exc:`sqlalchemy.orm.exc.MultipleResultsFound` if
    multiple results are found.
    `model` is the SQLAlchemy model on which to create a query.
    
    When building the query, filters are applied first, then sorting.
    Raises :exc:`UnknownField` if one of the named fields given in one
    of the `filters` does not exist on the `model`.
    Raises one of :exc:`AttributeError`, :exc:`KeyError`, or :exc:`TypeError`
    if there is a problem creating the query.
    """
    query = session_query(session, model)

    try:
        # Filter the query.
        filters = [Filter.from_dictionary(model, f) for f in filters]

        # This function call may raise an exception.
        filters = [create_filter(model, f) for f in filters]
    except UnknownField as e:
        raise BadRequest(cause=e, details=f'Invalid filter object: No such field "{e.field}"') from e
    except Exception as e:
        raise BadRequest(cause=e, details='Unable to construct query') from e

    query = query.filter(*filters)
    
    pks = primary_key_names(model)
    pk_order = (getattr(model, field).asc() for field in pks)
    query = query.order_by(*pk_order)

    return query