import bpy, bmesh

'''
BEGIN GPL LICENSE BLOCK

This program is free software; you can redistribute it and/or
modify it under the terms of the GNU General Public License
as published by the Free Software Foundation; either version 2
of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.    See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program; if not, write to the Free Software Foundation,
Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.

END GPL LICENCE BLOCK
'''

bl_info = {  
 "name": "create bounds of selected mesh",  
 "author": "Diego Quevedo ( http://doshape.com/ )",  
 "version": (1, 0),  
 "blender": (2, 7 , 8),  
 "location": "View3D > EditMode > tools",  
 "description": "create bounds of selected mesh",  
 "warning": "",  
 "wiki_url": "",  
 "tracker_url": "",  
 "category": "Doshape"} 

import bpy
import bmesh
import mathutils
import math
from bpy_extras.object_utils import AddObjectHelper, object_data_add

addon_keymaps = []
def shortcut(activar):   
    if activar:
         # handle the keymap
        wm = bpy.context.window_manager
        km = wm.keyconfigs.addon.keymaps.new(name='3D View', space_type='VIEW_3D')

        kmi = km.keymap_items.new(CreateBoundOperator.bl_idname, 'W', 'ANY', any=False, shift=False, ctrl=False, alt=True, oskey=False, key_modifier='NONE', head=False)
        
        addon_keymaps.append((km, kmi))
    else:
            # handle the keymap
        for km, kmi in addon_keymaps:
            km.keymap_items.remove(kmi)
        
        addon_keymaps.clear()



def add_object(self, context,  objt, vertices):

    oa = bpy.context.active_object
    obj = bpy.context.object
    me = obj.data
    bm = bmesh.from_edit_mesh(me)
    # Modify the BMesh, can do anything here...
    #print(vertices)
    c=0
    while c<8:
        print(vertices[c])
        bm.verts.new(vertices[c])
        c+=1
    
    #for v in bm.verts:
       # print(v.co)
       # c+=1
    
    #bm.faces.new((bm.verts[i] for i in range(-3,0)))


    # Finish up, write the bmesh back to the mesh
    bmesh.update_edit_mesh(me, True) 
    
class CreateBoundOperator(bpy.types.Operator):
    "Selected Vertex By Plane Side"
    bl_idname = 'mesh.create_bound'
    bl_label = 'create bounds of selected mesh'
    bl_description  = "allow create bounds of selected mesh"
    bl_options = {'REGISTER', 'UNDO'}
    



    def main(self, context):
    
        oa = bpy.context.active_object
        obj = bpy.context.object
        me = obj.data
        bm = bmesh.from_edit_mesh(me)
        selected_verts = [v for v in bm.verts if v.select]
        bmesh.update_edit_mesh(me, True) 
        
        
        print("#"*50)
        print(len(selected_verts))
        if len(selected_verts)>0:
            originales = []
            #cordenadas = []
            
            #obj = bpy.context.object
            bo = bpy.ops
            for obj in bpy.context.selectable_objects:
                originales.append(obj.name)
                
            bo.object.vertex_group_assign_new()
            bo.mesh.duplicate()
            
            

            bo.mesh.separate(type='SELECTED')        
            bo.object.mode_set(mode = 'OBJECT') 
            
            #oa.hide_select=True        
            bo.object.select_all(action='DESELECT')
            
            for objt in bpy.context.selectable_objects:
                
                if objt.name not in originales:
                    # selection
                    bpy.data.objects[objt.name].select = True         
                    bpy.context.scene.objects.active = bpy.data.objects[objt.name] 
                    objt.select=True
                    om = objt.matrix_world
                    cordenadas = [om * mathutils.Vector(v) for v in objt.bound_box]
                       
                    bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY', center='BOUNDS')

                    bo.object.mode_set(mode = 'EDIT')      
                    bo.mesh.select_all(action='SELECT')
                    bo.mesh.delete(type='VERT')

                    add_object(self, context, objt, cordenadas)
                    bo.object.mode_set(mode = 'OBJECT') 
                    bpy.ops.object.origin_set(type='GEOMETRY_ORIGIN', center='BOUNDS')

                    bpy.context.object.draw_type = 'BOUNDS'
                     

            
            bo.object.select_all(action='DESELECT')
            bpy.context.scene.objects.active = bpy.data.objects[oa.name]
            oa.hide_select=False 
            #oa.select=True
            bo.object.mode_set(mode = 'EDIT')  
        
        
    @classmethod
    def poll(self, context):
        obj = context.active_object
        
        return all([obj is not None, obj.type == 'MESH', obj.mode == 'EDIT'])

    def execute(self, context):
        
        self.main(context)
        return {'FINISHED'}
    
    
def menu_draw(self, context):
        self.layout.operator(CreateBoundOperator.bl_idname)

        


         
  
class CreateBoundOperatorPanel(bpy.types.Panel):
	#bl_category = "Bisector"
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"

    #bl_context = "editmode"
    bl_label = "bound Mesh"
    @classmethod
    def poll(cls, context):
        
        return (context.mode == 'EDIT_MESH'  )
    
    def draw(self, context):
        layout = self.layout
 
        row = layout.row(align=True)
        row.operator(CreateBoundOperator.bl_idname) #boud mesh 
        
   
    

def register():
    bpy.utils.register_module(__name__)
    
    bpy.types.VIEW3D_MT_edit_mesh.prepend(menu_draw)
    shortcut(True)



    
def unregister():
    bpy.utils.unregister_module(__name__)
    bpy.types.VIEW3D_MT_edit_mesh.remove(menu_draw)
    shortcut(False)

if __name__ == "__main__":
    register()
