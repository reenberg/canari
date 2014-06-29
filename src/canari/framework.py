#!/usr/bin/env python

from canari.resource import external_resource
from canari.utils.stack import calling_package
from canari.maltego import message

from subprocess import PIPE, Popen
import os
import re


__author__ = 'Nadeem Douba'
__copyright__ = 'Copyright 2012, Canari Project'
__credits__ = []

__license__ = 'GPL'
__version__ = '0.3'
__maintainer__ = 'Nadeem Douba'
__email__ = 'ndouba@gmail.com'
__status__ = 'Development'

__all__ = [
    'superuser',
    'deprecated',
    'configure',
    'ExternalCommand'
]


def superuser(f):
    f.privileged = True
    return f


def deprecated(f):
    f.deprecated = True
    return f


class configure(object):
    def __init__(self, **kwargs):
        if not kwargs.has_key('label'):
            raise TypeError('Missing transform specification property: "label"')

        if kwargs.has_key('spec'):
            # New style specification (list of triples)
            if not isinstance(kwargs['spec'], list):
                raise TypeError('Expected "spec" of type list (got %s instead)' % type(kwargs['spec']).__name__)
            if len(kwargs['spec']) < 1:
                raise ValueError('Expected "spec" to contain atleast one element (got %s instead)' % len(kwargs['spec']))

            # After verifying the types we wan't to unpack the spec list, to be
            # backwards compatible.
            kwargs['uuids'] = []
            kwargs['inputs'] = []

            for elem in kwargs['spec']:
                if not len(elem) == 3:
                    raise ValueError('Expected exactly three values for each element of the "spec" list (got %s instead)' % len(elem))

                uuid, input, transform_sets = elem

                if not isinstance(uuid, str):
                    raise TypeError('Expected uuid part of the "spec" list to be of type string (got %s instead)' % type(uuid).__name__)
                if not isinstance(input, message.MetaEntityClass):
                    raise TypeError('Expected input part of the "spec" list to be an entity (got %s instead)' % type(input).__name__)
                if not isinstance(transform_sets, list):
                    raise TypeError('Expected transform sets part of the "spec" list to be of type list (got %s instead)' % type(transform_sets).__name__)

                # If the user specified an empty list as the transform set, then
                # add the empty string to the list, so we always have at least
                # one element.
                if not transform_sets: # Empty list
                    transform_sets.append('')
                for tset in transform_sets:
                    if not isinstance(tset, str):
                        raise TypeError('Expected elements of transform set to be of type string (got %s instead)' % type(tset).__name__)

                # 'Unpack' this element, so we remain backwards compatible.
                kwargs['uuids'].append(uuid)
                kwargs['inputs'].append((transform_sets[0], input))
        else:
            # Old style specification
            if not kwargs.has_key('uuids'):
                raise TypeError('Missing transform specification property: "uuids"')
            if not isinstance(kwargs['uuids'], list):
                raise TypeError('Expected "uuids" property to be of type list (got %s instead)' % type(kwargs['uuids']).__name__)
            if not kwargs.has_key('inputs'):
                raise TypeError('Missing transform specification property: "inputs"')
            if not isinstance(kwargs['inputs'], list):
                raise TypeError('Expected "inputs" property to be of type list (got %s instead)' % type(kwargs['inputs']).__name__)

        # Set optional fields
        kwargs['owner'] = kwargs.get('owner', '')
        kwargs['description'] = kwargs.get('description', '')
        kwargs['disclaimer'] = kwargs.get('disclaimer', '')
        kwargs['outputs'] = kwargs.get('outputs', ['Any'])
        kwargs['debug'] = kwargs.get('debug', False)
        kwargs['remote'] = kwargs.get('remote', False)
        self.function = kwargs.get('cmd', None)
        # Temporarily store kwargs, so we may use them later when we are
        # actually @decorating the function.
        self._kwargs = kwargs

    def __call__(self, f):
        if callable(self.function):
            self.function.__dict__.update(f.__dict__)
            f = self.function
        f.__dict__.update(self._kwargs)
        return f


class ExternalCommand(object):
    def __init__(self, transform_name, transform_args=None, interpreter=None, is_resource=True):
        if transform_args is None:
            transform_args = []
        self._extra_external_args = []

        if interpreter is not None:
            self._extra_external_args.append(interpreter)
            libpath = external_resource(
                os.path.dirname(transform_name),
                '%s.resources.external' % calling_package()
            )
            if interpreter.startswith('perl') or interpreter.startswith('ruby'):
                self._extra_external_args.extend(['-I', libpath])
            elif interpreter.startswith('java'):
                self._extra_external_args.extend(['-cp', libpath])

        if ' ' in transform_name:
            raise ValueError('Transform name %s cannot have spaces.' % repr(transform_name))
        elif not is_resource:
            self._extra_external_args.append(transform_name)
        else:
            self._extra_external_args.append(
                external_resource(
                    transform_name,
                    '%s.resources.external' % calling_package()
                )
            )

        if isinstance(transform_args, basestring):
            self._extra_external_args = re.split(r'\s+', transform_args)
        else:
            self._extra_external_args.extend(transform_args)

    def __call__(self, request, request_xml):
        args = [request.value]
        if isinstance(request.params, list) and request.params:
            args.extend(request.params)
        if request.fields:
            args.append('#'.join(['%s=%s' % (k, v) for k, v in request.fields.iteritems()]))
        if isinstance(request_xml, basestring):
            p = Popen(self._extra_external_args + list(args), stdin=PIPE, stdout=PIPE)
            out, err = p.communicate(request_xml)
            return out
        p = Popen(self._extra_external_args + list(args))
        p.communicate()
        exit(p.returncode)
