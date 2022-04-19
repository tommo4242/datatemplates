import os
from treelib import Tree
from bs4 import BeautifulSoup
import urllib.parse
from py_jama_rest_client.client import JamaClient


class UBXJamaClient(JamaClient):
    """
    This class adds to the base class so that we don't have to fork
    https://github.com/jamasoftware-ps/py-jama-rest-client
    """

    def get_attachment_file(self, url):

        resource_path = r'files'
        params = {'url': url}
        attachment = self._JamaClient__core.get(resource_path, params=params)

        return attachment


class JamaProject:
    """
    Comprehensive abstraction of the Jama Project entity
    """

    info = None
    items = None

    pick_lists = None
    pick_lists_by_id = None
    pick_lists_options = None
    users_by_id = dict()
    releases = None

    instance_item_types = None
    instance_item_types_by_id = None
    item_types = None
    prj_id = 0
    client: UBXJamaClient = None

    def __init__(self, url: str, auth, prj_id: int):
        self.prj_id = prj_id
        self.client = UBXJamaClient(url, credentials=auth, oauth=True)
        self.fetch_instance_item_types()

    def fetch_item_types(self):
        if self.item_types is None:
            self.item_types = self.client.get_project_item_types(self.prj_id)
        return self.item_types

    def fetch_instance_item_types(self):
        if self.instance_item_types is None:
            self.instance_item_types_by_id = dict()
            self.instance_item_types = self.client.get_item_types()
            for x in self.instance_item_types:
                self.instance_item_types_by_id[x['id']] = x
        return self.instance_item_types

    def get_item_type_by_key(self, key: str):
        if self.instance_item_types_by_id is None:
            raise Exception(f"Item Type #{key} not found")

        result = next((x for x in self.instance_item_types
                       if x["typeKey"] == key), None)

        if result is None:
            raise Exception(f"Item Type #{key} not found")

        return result

    def get_item_type(self, item_id):
        if self.instance_item_types_by_id is None:
            raise Exception(f"Item Type #{item_id} not found")

        result = next((x for x in self.instance_item_types
                       if x["id"] == item_id), None)

        if result is None:
            raise Exception(f"Item Type #{item_id} not found")

        return result

    def fetch_item_by_id(self, item_id):
        try:
            item = self.client.get_item(item_id)
        except Exception:
            item = None
        finally:
            return item

    def fetch_items(self):
        if self.items is None or len(self.items) <= 0:
            self.items = self.client.get_items(self.prj_id)
        return self.items

    def fetch_attachments(self, attachment_id):
        attachments = self.client.get_attachment(attachment_id)
        return attachments

    def get_attachment_file(self, url):
        attachment_file = self.client.get_attachment_file(url)
        return attachment_file

    def get_attachments_from_item(self, item_id):
        item_attachments = self.client.get_attachments_from_item(item_id)
        return item_attachments

    def get_tags(self, project):
        tag_data = self.client.get_tags(project)
        return tag_data

    def get_relationship_types(self):
        item_types = self.client.get_relationship_types()
        return item_types

    def get_items_upstream_relationships(self, item_id):
        upstream_relationships = \
            self.client.get_items_upstream_relationships(item_id)
        return upstream_relationships

    def get_tagged_items(self, tag_id):
        tagged_items = self.client.get_tagged_items(tag_id)
        return tagged_items

    def fetch_releases(self):
        if self.releases is None:
            self.releases = self.client.get_releases(self.prj_id)

        return self.releases

    def fetch_pick_lists(self):
        if self.pick_lists is None:
            self.pick_lists = self.client.get_pick_lists()
            self.pick_lists_options = dict()
            self.pick_lists_by_id = dict()

        for p in self.pick_lists:
            pick_list_id = p["id"]
            if str(pick_list_id) not in self.pick_lists_options:
                options = self.client.get_pick_list_options(str(pick_list_id))
                self.pick_lists_options[pick_list_id] = options
            else:
                options = self.pick_lists_options[str(pick_list_id)]

            self.pick_lists_by_id[pick_list_id] = p

        return self.pick_lists

    def get_user_by_id(self, user_id):
        if self.users_by_id.get(user_id, None) is None:
            self.users_by_id[user_id] = self.client.get_user(user_id)
        return self.users_by_id[user_id]

    def get_items_workflow_transition_options(self, item_id):
        workflow_transition_options = \
            self.client.get_items_workflow_transition_options(item_id)
        return workflow_transition_options

    def get_item_comments(self, item_id):
        item_comments = self.client.get_item_comments(item_id)
        return item_comments

    def get_info(self):
        if self.info is None:
            self.info = self.client.get_project(self.prj_id)
        return self.info


class DocItem:
    """
    Represents a Jama Item extracted from Jama and placed into a tree structure
    to capture the correct document sequence.
    """
    id: str
    item: None
    item_type: None
    fields: dict()
    sequence: str
    documentKey: str
    createdBy: None
    modifiedBy: None

    def __init__(self, ctx: JamaProject, item=None, attachment_dir=r"jama/"):
        self.ctx = ctx
        self.attachment_dir = attachment_dir
        if item is not None:
            self.id = item['id']
            self.item = item
            self.item_type = ctx.get_item_type(item['itemType'])
            self.fields = item['fields']
            self.sequence = item['location']['sequence']
            self.documentKey = item['documentKey']
            self.createdBy = ctx.get_user_by_id(item['createdBy'])
            self.modifiedBy = ctx.get_user_by_id(item['modifiedBy'])
        else:
            self.id = 0
            self.item = None
            self.item_type = None
            self.fields = None
            self.sequence = ""
            self.documentKey = ""
            self.createdBy = None
            self.modifiedBy = None
        return

    def is_folder(self):
        if self.item_type['typeKey'] == 'FLD':
            return True
        else:
            return False

    def is_set(self):
        if self.item_type['typeKey'] == 'SET':
            return True
        else:
            return False

    def has_fld(self, fld_name) -> bool:
        if fld_name in self.fields:

            if str(self.fields[fld_name]) == "":
                return False

            return True
        else:
            return False

    def transform_html(self, html: str) -> str:
        """
        Transforms rich text fields when they are queried. A side effect is to
        copy linked images into the attachment directory.
        """
        if html == "":
            return ""

        soup = BeautifulSoup(html, features="lxml")

        # Lower the level of any headings in the text
        for i in range(10, 0, -1):
            for tag in soup.findAll(f'h{i}'):
                tag.name = f"h{i + self.level()}"

        # Copy over any referenced image files
        for img in soup.findAll('img'):
            src = img['src']
            dst = os.path.join(self.attachment_dir, os.path.basename(src))
            dst = urllib.parse.unquote(dst)
            attachment_file = self.ctx.get_attachment_file(src)
            if not os.path.exists(self.attachment_dir):
                os.makedirs(self.attachment_dir, exist_ok=True)
            with open(dst, 'wb') as handler:
                handler.write(attachment_file.content)

            img['src'] = dst
            img['class'] = \
                img.get('class', []) + ['keep-together', 'keep-image-balance']

        resulting_html = ""
        for c in soup.body.contents:
            try:
                c['class'] = \
                    c.get('class', []) + ['keep-together',
                                          'keep-font-size-balance']
            except Exception:
                pass
            resulting_html += str(c)

        return resulting_html

    def level(self):
        return self.sequence.count('.')+1

    def lbl(self, field_name):
        for fld in self.item_type['fields']:
            if (fld['name'] == field_name) \
               or (fld['name'] == field_name+'$'+str(self.item_type['id'])) \
               or (fld['label'] == field_name):
                return fld['label']

        return field_name

    def fld(self, field_name):
        for fld in self.item_type['fields']:

            if fld['name'] == field_name:
                key = field_name
            else:
                if fld['name'] == field_name + '$' + str(self.item_type['id']):
                    key = fld['name']
                else:
                    if fld['label'] == field_name:
                        key = fld['name']
                    else:
                        continue

            value = str(self.fields[key])

            if fld["fieldType"] == "TEXT" and fld["textType"] == "RICHTEXT":
                return self.transform_html(value)
            else:
                return value

        return ""


def sort_node_by_sequence(node):
    seq = node.data.item['location']['sequence']
    parts = seq.split('.')
    padded_seq = ""
    for s in parts:
        if padded_seq == "":
            padded_seq += s.zfill(5)
        else:
            padded_seq += "."+s.zfill(5)
    return padded_seq


def find_node_by_key(tree: Tree, documentKey):
    for item in tree.all_nodes():
        if (item.data.documentKey == documentKey):
            return item.identifier
    return None


def snapshot(url, auth, prj_id, start_node, attachment_dir=r"jama"):

    ctx = JamaProject(url, auth, prj_id)
    ctx.fetch_items()

    document_tree = Tree()
    root_item = DocItem(ctx)
    root = document_tree.create_node(
                identifier=f'PRJ: {ctx.prj_id}', data=root_item)

    for src_item in ctx.items:
        new_node = DocItem(ctx, src_item, attachment_dir)
        # Match Hierarchy
        if 'item' in src_item['location']['parent']:
            src_parent_item_id = src_item['location']['parent']['item']
            src_parent_node = document_tree.get_node(src_parent_item_id)
            if src_parent_node is None:
                raise Exception(f"Items not mapped src #{src_parent_item_id}")
            document_tree.create_node(
                tag=src_item['documentKey'],
                identifier=src_item["id"],
                data=new_node,
                parent=src_parent_node)

        else:
            document_tree.create_node(
                tag=src_item['documentKey'],
                identifier=src_item["id"],
                data=new_node,
                parent=root)

    # document_tree.show(key=sort_node_by_sequence, data_property='sequence')

    section_nid = find_node_by_key(document_tree, start_node)
    section = document_tree.subtree(section_nid)
    return_list = []
    for item in section.expand_tree(key=sort_node_by_sequence):
        return_list.append(section.get_node(item).data)
    return return_list

# if __name__ == "__main__":
#     data = snapshot(
#               'https://jama.u-blox.net',
#               ('0enjieniq1dsusr', 'gej5uqkp1lobwmi1yyam8a3g4'),
#               58, 'UBX_P4-SET-2', r"jama")
#     for item in data:
#         print(item.sequence,
#           item.fld('name'), '('+item.fld('documentKey')+')')
#         print(item.fld('description'))
