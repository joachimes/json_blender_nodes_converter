import bpy
import json 


def get_base_node_attr(modifier) -> list[str]:
    # Create basic attribute node
    node_base = modifier.node_group.nodes.new('ShaderNodeCombineXYZ')
    node_base_attribs = dir(node_base)
    modifier.node_group.nodes.remove(node_base)
    return node_base_attribs

def extract_uniq_node_attributes(node_new, basenode_attr:list) -> dict:
    # Node information
    uniq_attr = {}
    for attr in dir(node_new):
        if attr not in basenode_attr:
            uniq_attr[attr] = getattr(node_new, attr)
    return uniq_attr

def convert_nodes_to_json(obj, file=None) -> list[dict]:
    node_group_list = []
    for modifier in obj.modifiers:
        if modifier.type != "NODES":
            continue
        nodes_obj = {}
        links_obj = {}

        node_base_attribs = get_base_node_attr(modifier)

        for i, link in enumerate(modifier.node_group.links):
            # Node information
            if link.from_node.name not in nodes_obj:
                node_new = modifier.node_group.nodes[link.from_node.name]
                uniq_attr = extract_uniq_node_attributes(node_new, node_base_attribs)
                nodes_obj[link.from_node.name] = {'bl_idname': link.from_node.bl_idname, 'uniq_attr': uniq_attr}
            if link.to_node.name not in nodes_obj:
                node_new = modifier.node_group.nodes[link.to_node.name]
                uniq_attr = extract_uniq_node_attributes(node_new, node_base_attribs)
                nodes_obj[link.to_node.name] = {'bl_idname': link.to_node.bl_idname, 'uniq_attr': uniq_attr}

            
            # Socket information
            links_obj[i] = {'output': [link.from_node.name, link.from_socket.name], 'input': [link.to_node.name, link.to_socket.name]}
        
        node_group_list.append({'nodes_obj': nodes_obj, 'links_obj': links_obj})
    return node_group_list
        

def convert_nodes_from_json(obj, node_list, file="temp"):
    # with open(file) as f:
        # data = json.load(f)

    for node_group in node_list:
        geonode_modifier = obj.modifiers.new(obj.name+file, 'NODES')
        # Remove initial nodes
        for node in geonode_modifier.node_group.nodes:
            geonode_modifier.node_group.nodes.remove(node)

        # Add all nodes
        for node_name in node_group['nodes_obj']:
            node_dict = node_group['nodes_obj'][node_name]
            new_node = geonode_modifier.node_group.nodes.new(node_dict['bl_idname'])
            if node_dict['bl_idname'] not in ['NodeGroupOutput', 'NodeGroupInput']:
                for attr in node_dict['uniq_attr']:
                    try:
                        attr_val = node_dict['uniq_attr'][attr]
                        setattr(new_node, attr, attr_val)
                    except AttributeError:
                        continue
            new_node.name = node_name

        for link_num in node_group['links_obj']:
            link = node_group['links_obj'][link_num]
            print(link)
            if link['input'][1] not in geonode_modifier.node_group.nodes[link['input'][0]].inputs:
                input_type = geonode_modifier.node_group.nodes[link['output'][0]].outputs[link['output'][1]].type
                geonode_modifier.node_group.nodes[link['input'][0]].inputs.new(input_type, link['input'][1])
            socket_input = geonode_modifier.node_group.nodes[link['input'][0]].inputs[link['input'][1]]

            if link['output'][1] not in geonode_modifier.node_group.nodes[link['output'][0]].outputs:
                output_type = geonode_modifier.node_group.nodes[link['input'][0]].inputs[link['input'][1]].type
                geonode_modifier.node_group.nodes[link['output'][0]].outputs.new(output_type, link['output'][1])
            socket_output = geonode_modifier.node_group.nodes[link['output'][0]].outputs[link['output'][1]]

            geonode_modifier.node_group.links.new(socket_input, socket_output)


plane = bpy.data.objects['Plane']

node_group_list = convert_nodes_to_json(plane)
convert_nodes_from_json(plane, node_group_list)


