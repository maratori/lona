from textwrap import indent

from lona.html.attribute_dict import AttributeDict
from lona.html.attribute_list import AttributeList
from lona.html.abstract_node import AbstractNode
from lona.html.text_node import TextNode
from lona.html.node_list import NodeList
from lona.protocol import NodeType


class Node(AbstractNode):
    TAG_NAME = 'html'
    SINGLE_TAG = False
    ATTRIBUTES = {}
    ID_LIST = []
    CLASS_LIST = []
    STYLE = {}
    LONA_CLASS_LIST = []

    def __init__(self, *args, **kwargs):
        self._id = self.gen_id()

        self._id_list = AttributeList(self, self.ID_LIST)
        self._class_list = AttributeList(self, self.CLASS_LIST)
        self._style = AttributeDict(self, self.STYLE)
        self._attributes = AttributeDict(self, self.ATTRIBUTES)
        self._nodes = NodeList(self)

        # lona classes
        for class_name in self.LONA_CLASS_LIST:
            if class_name in ('clickable', 'changeable'):
                setattr(self, class_name, True)

        # args (nodes)
        for arg in args:
            if not isinstance(arg, (AbstractNode, str)):
                arg = str(arg)

            if isinstance(arg, str):
                arg = TextNode(arg)

            self.append(arg)

        # kwargs (attributes)
        for name, value in kwargs.items():

            # remove underscores from attributes
            # this makes kwargs like '_class' possible to prevent clashes
            # with python grammar
            if '_' in name:
                name = name.replace('_', '-')

                if name.startswith('-'):
                    name = name[1:]

            # lona classes
            if name in ('clickable', 'changeable'):
                setattr(self, name, value)

            # change aware attributes
            elif name == 'id':
                if not isinstance(value, list):
                    value = [value]

                self._id_list._reset(value)

            elif name == 'class':
                if not isinstance(value, list):
                    value = [value]

                self._class_list._reset(value)

            elif name == 'style':
                if not isinstance(value, dict):
                    raise ValueError('style has to be dict')

                self._style._reset(value)

            elif name == 'nodes':
                if not isinstance(value, list):
                    value = [value]

                self._nodes._reset(value)

            # misc attributes
            else:
                self._attributes[name] = value

    # node attributes  ########################################################
    # id_list
    @property
    def id_list(self):
        return self._id_list

    @id_list.setter
    def id_list(self, value):
        self._id_list._reset(value)

    # class_list
    @property
    def class_list(self):
        return self._class_list

    @class_list.setter
    def class_list(self, value):
        self._class_list._reset(value)

    # style
    @property
    def style(self):
        return self._style

    @style.setter
    def style(self, value):
        self._style._reset(value)

    # attributes
    @property
    def attributes(self):
        return self._attributes

    @attributes.setter
    def attributes(self, value):
        self._attributes._reset(value)

    # nodes
    @property
    def nodes(self):
        return self._nodes

    @nodes.setter
    def nodes(self, value):
        self._nodes._reset(value)

    # lona attribute helper ###################################################
    def has_class(self, class_name):
        return class_name in self._class_list

    def has_id(self, id_name):
        return id_name in self._id_list

    # lona attributes #########################################################
    @property
    def clickable(self):
        return 'lona-clickable' in self._class_list

    @clickable.setter
    def clickable(self, value):
        if value:
            self._class_list.add('lona-clickable')

        else:
            self._class_list.remove('lona-clickable')

    @property
    def changeable(self):
        return 'lona-changeable' in self._class_list

    @changeable.setter
    def changeable(self, value):
        if value:
            self._class_list.add('lona-changeable')

        else:
            self._class_list.remove('lona-changeable')

    # serialisation ###########################################################
    def _has_changes(self):
        return any([
            self._id_list._has_changes(),
            self._class_list._has_changes(),
            self._style._has_changes(),
            self._attributes._has_changes(),
            self._nodes._has_changes(),
        ])

    def _get_changes(self):
        return [
            self._id,
            self._id_list._get_changes(),
            self._class_list._get_changes(),
            self._style._get_changes(),
            self._attributes._get_changes(),
            self._nodes._get_changes(),
        ]

    def _clear_changes(self):
        self._id_list._clear_changes()
        self._class_list._clear_changes()
        self._style._clear_changes()
        self._attributes._clear_changes()
        self._nodes._clear_changes()

    def _serialize(self):
        return [
            NodeType.NODE,
            self._id,
            self.TAG_NAME,
            self._id_list._serialize(),
            self._class_list._serialize(),
            self._style._serialize(),
            self._attributes._serialize(),
            self._nodes._serialize(),
        ]

    # node list helper ########################################################
    def insert(self, index, node):
        self._nodes.insert(index, node)

    def append(self, node):
        self._nodes.append(node)

    def remove(self, node=None):
        if not node:
            if not self._parent:
                raise RuntimeError('node has no parent node')

            self._parent.remove(self)

            return

        self._nodes.remove(node)

    def clear(self):
        self._nodes.clear()

    def set_text(self, text):
        self.nodes = [str(text)]

    def __getitem__(self, index):
        return self._nodes[index]

    def __setitem__(self, index, value):
        self._nodes[index] = value

    def __iter__(self):
        return self._nodes.__iter__()

    def __len__(self):
        return self._nodes.__len__()

    # string representation ###################################################
    def __str__(self):
        with self.document.lock():
            # opening tag
            string = '<{} id="lona-#{}{}{}"'.format(
                self.TAG_NAME,
                self._id,
                ' ' if self.id_list else '',
                self.id_list,
            )

            if self.class_list:
                string += ' class="{}"'.format(str(self.class_list))

            if self.style:
                string += ' style="{}"'.format(
                    self.style.to_sub_attribute_string())

            if self.attributes:
                string += ' '
                string += self.attributes.to_attribute_string()

            if self.SINGLE_TAG:
                string += ' />'

            else:
                string += '>'

            # nodes
            if self.nodes:
                string += '\n'
                string += indent(str(self.nodes), '  ')
                string += '\n'

            # closing tag
            if not self.SINGLE_TAG:
                string += '</{}>'.format(self.TAG_NAME)

            return string

    def __repr__(self):
        return self.__str__()