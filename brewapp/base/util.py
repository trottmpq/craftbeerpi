import csv
import datetime
import os.path
import time
from functools import update_wrapper, wraps

from flask import json, make_response

from .. import app, db


def getAsArray(obj, order=None):
    if order:
        result = obj.query.order_by(order).all()
    else:
        result = obj.query.all()
    ar = []
    for t in result:
        ar.append(to_dict(t))
    return ar


def getAsDict(obj, key, deep=None, order=None):
    if order:
        result = obj.query.order_by(order).all()
    else:
        result = obj.query.all()
    ar = {}
    for t in result:
        ar[getattr(t, key)] = to_dict(t, deep=deep)
    return ar


def setTargetTemp(kettleid, temp):
    if kettleid:
        if app.brewapp_target_temp_method is not None:
            app.brewapp_target_temp_method(kettleid, temp)


# Job Annotaiton
# key = uniquie key as string
# interval = interval in which the method is invoedk
def brewjob(key, interval, config_parameter = None):
    def real_decorator(function):
        app.brewapp_jobs.append(
            {
                "function": function,
                "key": key,
                "interval": interval,
                "config_parameter": config_parameter
            }
        )
        def wrapper(*args, **kwargs):
            function(*args, **kwargs)

        return wrapper

    return real_decorator


# Init Annotaiton
def brewinit(order = 0, config_parameter = None):
    def real_decorator(function):
        app.brewapp_init.append(
            {
                "function": function,
                "order": order,
                "config_parameter": config_parameter
            }
        )
        def wrapper(*args, **kwargs):
            function(*args, **kwargs)

        return wrapper

    return real_decorator


def config(name):
    def real_decorator(function):
        def wrapper(*args, **kwargs):
            if(app.brewapp_config.get(name, 'No') == 'Yes'):
                function(*args, **kwargs)

        return wrapper

    return real_decorator


def brewautomatic():
    def real_decorator(function):
        app.brewapp_pid.append(function)
        def wrapper(*args, **kwargs):
            function(*args, **kwargs)
        return wrapper

    return real_decorator


def controllerLogic():
    def real_decorator(function):
        app.brewapp_controller[function.__name__] = function
        def wrapper(*args, **kwargs):
            function(*args, **kwargs)
        return wrapper

    return real_decorator


def timing(f):
    def wrap(*args):
        time1 = time.time()
        ret = f(*args)
        time2 = time.time()

        return ret
    return wrap


def writeTempToFile(file, timestamp, current_temp, target_temp):
    filename = f"log/{file}.templog"
    '''

    if os.path.isfile(filename) == False:
        with open(filename, "a") as myfile:
            myfile.write("Date,Current Temperature,Target Temperature\n")
    '''
    formatted_time = datetime.datetime.fromtimestamp((timestamp / 1000)).strftime('%Y-%m-%d %H:%M:%S')
    tt = "0" if target_temp is None else str(target_temp)
    msg = formatted_time + "," + str(current_temp) + "," + tt + "\n"

    with open(filename, "a") as myfile:
        myfile.write(msg)


def writeSpindle(file, timestamp, current_temp, wort, battery):
    filename = f"log/{file}.templog"

    '''
    if os.path.isfile(filename) == False:
        with open(filename, "a") as myfile:
            myfile.write("Date,Current Temperature,Wort,Battery\n")
    '''
    formatted_time = datetime.datetime.fromtimestamp((timestamp / 1000)).strftime('%Y-%m-%d %H:%M:%S')
    msg = formatted_time + "," + str(current_temp) + "," + str(wort) + "," + str(battery) + "\n"

    with open(filename, "a") as myfile:
        myfile.write(msg)


def read_hydrometer_log(file):

    if os.path.isfile(file) == False:
        return

    array = {"hydrometer_temp": [], "wort": [], "battery": []}

    with open(file, 'rb') as f:
        reader = csv.reader(f)
        for row in reader:
            #print row
            time = int((datetime.datetime.strptime(row[0], "%Y-%m-%d %H:%M:%S") - datetime.datetime(1970, 1, 1)).total_seconds()) * 1000
            array["hydrometer_temp"].append([time, float(row[1])])
            array["wort"].append([time, float(row[2])])
            array["battery"].append([time, float(row[3])])
    return array


def read_temp_log(file):
    result = {"temp": [], "target_temp": []}

    if os.path.isfile(file) == False:
        return result
    with open(file, 'rb') as f:
        reader = csv.reader(f)
        for row in reader:
            #print row
            time = int((datetime.datetime.strptime(row[0], "%Y-%m-%d %H:%M:%S") - datetime.datetime(1970, 1, 1)).total_seconds()) * 1000
            result["temp"].append([time, float(row[1])])

            result["target_temp"].append([time, float(row[2])])
    return result


def delete_file(file):
    if os.path.isfile(file) == True:

        os.remove(file)


def updateModel(model, id, json):
    m = model.query.get(id)
    m.decodeJson(json)
    db.session.commit()
    return to_dict(m)


def createModel(model, json):
    m = model()
    m.decodeJson(json)
    db.session.add(m)
    db.session.commit()
    return to_dict(m)


def deleteModel(model, id):
    try:
        model.query.filter_by(id=id).delete()
        db.session.commit()
        return True
    except:
        return False


def nocache(view):
    @wraps(view)
    def no_cache(*args, **kwargs):
        response = make_response(view(*args, **kwargs))
        response.headers['Last-Modified'] = datetime.datetime.now()
        response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, post-check=0, pre-check=0, max-age=0'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = '-1'
        return response

    return update_wrapper(no_cache, view)

# This code was adapted from :meth:`elixir.entity.Entity.to_dict` and
# http://stackoverflow.com/q/1958219/108197.
def to_dict(instance, deep=None, exclude=None, include=None,
            exclude_relations=None, include_relations=None,
            include_methods=None):
    """Returns a dictionary representing the fields of the specified `instance`
    of a SQLAlchemy model.

    The returned dictionary is suitable as an argument to
    :func:`flask.jsonify`; :class:`datetime.date` and :class:`uuid.UUID`
    objects are converted to string representations, so no special JSON encoder
    behavior is required.

    `deep` is a dictionary containing a mapping from a relation name (for a
    relation of `instance`) to either a list or a dictionary. This is a
    recursive structure which represents the `deep` argument when calling
    :func:`!_to_dict` on related instances. When an empty list is encountered,
    :func:`!_to_dict` returns a list of the string representations of the
    related instances.

    If either `include` or `exclude` is not ``None``, exactly one of them must
    be specified. If both are not ``None``, then this function will raise a
    :exc:`ValueError`. `exclude` must be a list of strings specifying the
    columns which will *not* be present in the returned dictionary
    representation of the object (in other words, it is a
    blacklist). Similarly, `include` specifies the only columns which will be
    present in the returned dictionary (in other words, it is a whitelist).

    .. note::

       If `include` is an iterable of length zero (like the empty tuple or the
       empty list), then the returned dictionary will be empty. If `include` is
       ``None``, then the returned dictionary will include all columns not
       excluded by `exclude`.

    `include_relations` is a dictionary mapping strings representing relation
    fields on the specified `instance` to a list of strings representing the
    names of fields on the related model which should be included in the
    returned dictionary; `exclude_relations` is similar.

    `include_methods` is a list mapping strings to method names which will
    be called and their return values added to the returned dictionary.

    """
    if (exclude is not None or exclude_relations is not None) and \
            (include is not None or include_relations is not None):
        raise ValueError('Cannot specify both include and exclude.')
    # create a list of names of columns, including hybrid properties
    instance_type = type(instance)
    columns = []
    try:
        inspected_instance = sqlalchemy_inspect(instance_type)
        column_attrs = inspected_instance.column_attrs.keys()
        descriptors = inspected_instance.all_orm_descriptors.items()
        hybrid_columns = [k for k, d in descriptors
                          if d.extension_type == hybrid.HYBRID_PROPERTY
                          and not (deep and k in deep)]
        columns = column_attrs + hybrid_columns
    except NoInspectionAvailable:
        return instance
    # filter the columns based on exclude and include values
    if exclude is not None:
        columns = (c for c in columns if c not in exclude)
    elif include is not None:
        columns = (c for c in columns if c in include)
    # create a dictionary mapping column name to value
    result = dict((col, getattr(instance, col)) for col in columns
                  if not (col.startswith('__') or col in COLUMN_BLACKLIST))
    # add any included methods
    if include_methods is not None:
        for method in include_methods:
            if '.' not in method:
                value = getattr(instance, method)
                # Allow properties and static attributes in include_methods
                if callable(value):
                    value = value()
                result[method] = value
    # Check for objects in the dictionary that may not be serializable by
    # default. Convert datetime objects to ISO 8601 format, convert UUID
    # objects to hexadecimal strings, etc.
    for key, value in result.items():
        if isinstance(value, (datetime.date, datetime.time)):
            result[key] = value.isoformat()
        elif isinstance(value, uuid.UUID):
            result[key] = str(value)
        elif key not in column_attrs and is_mapped_class(type(value)):
            result[key] = to_dict(value)
    # recursively call _to_dict on each of the `deep` relations
    deep = deep or {}
    for relation, rdeep in deep.items():
        # Get the related value so we can see if it is None, a list, a query
        # (as specified by a dynamic relationship loader), or an actual
        # instance of a model.
        relatedvalue = getattr(instance, relation)
        if relatedvalue is None:
            result[relation] = None
            continue
        # Determine the included and excluded fields for the related model.
        newexclude = None
        newinclude = None
        if exclude_relations is not None and relation in exclude_relations:
            newexclude = exclude_relations[relation]
        elif (include_relations is not None and
              relation in include_relations):
            newinclude = include_relations[relation]
        # Determine the included methods for the related model.
        newmethods = None
        if include_methods is not None:
            newmethods = [method.split('.', 1)[1] for method in include_methods
                          if method.split('.', 1)[0] == relation]
        if is_like_list(instance, relation):
            result[relation] = [to_dict(inst, rdeep, exclude=newexclude,
                                        include=newinclude,
                                        include_methods=newmethods)
                                for inst in relatedvalue]
            continue
        # If the related value is dynamically loaded, resolve the query to get
        # the single instance.
        if isinstance(relatedvalue, Query):
            relatedvalue = relatedvalue.one()
        result[relation] = to_dict(relatedvalue, rdeep, exclude=newexclude,
                                   include=newinclude,
                                   include_methods=newmethods)
    return result
