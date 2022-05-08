import bpy
import json 
def convert_nodes_to_json(obj, file=None):
    node_group_list = []
    for modifier in obj.modifiers:
        if modifier.type != "NODES":
            continue
        nodes_obj = {}
        links_obj = {}
        for i, link in enumerate(modifier.node_group.links):
            # Node information
            nodes_obj[link.from_node.name] = link.from_node.bl_idname
            nodes_obj[link.to_node.name] = link.to_node.bl_idname
            
            # Socket information
            links_obj[i] = {'output':[link.from_node.name, link.from_socket.name], 'input':[link.to_node.name, link.to_socket.name]}
        
        node_group_list.append({'nodes_obj':nodes_obj, 'links_obj':links_obj})
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
            new_node = geonode_modifier.node_group.nodes.new(node_group['nodes_obj'][node_name])
            new_node.name = node_name

        for link_num in node_group['links_obj']:
            link = node_group['links_obj'][link_num]
            socket_input = geonode_modifier.node_group.nodes[link['input'][0]].inputs[link['input'][1]]
            socket_output = geonode_modifier.node_group.nodes[link['output'][0]].outputs[link['output'][1]]

            geonode_modifier.node_group.links.new(socket_input, socket_output)


plane = bpy.data.objects['Plane']

node_group_list = convert_nodes_to_json(plane)
convert_nodes_from_json(plane, node_group_list)


