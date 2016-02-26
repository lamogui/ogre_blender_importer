
bl_info = {
    "name": "Ogre Blender Importer",
    "author": "Julien De Loor",
    "location": "File > Import-Export",
    "blender": (2,76,0),
    "category": "Import-Export"
}

import bpy
from OgreMeshSerializer import OgreMeshSerializer



class IMPORT_OT_ogre_mesh(bpy.types.Operator):
    bl_idname = "import.ogre_mesh";
    bl_label = "Import Ogre Mesh (.mesh)";
    bl_description = "Import mesh data from Ogre Mesh (.mesh files) V1.10";

    filename_ext = ".mesh";
    filter_glob = bpy.props.StringProperty(default="*.mesh", options={'HIDDEN'})
    filepath = bpy.props.StringProperty(name="File Path", subtype="FILE_PATH");

    def execute(self, context):
        meshfile = open(self.filepath,mode='rb');
        meshserializer = OgreMeshSerializer();
        meshserializer.disableValidation();
        meshserializer.importMesh(meshfile);
        return {'FINISHED'};


    def invoke(self, context, event):
        context.window_manager.fileselect_add(self);
        return {'RUNNING_MODAL'};


def menu_func_import_ogre_mesh(self, context):
    self.layout.operator(IMPORT_OT_ogre_mesh.bl_idname, text="Ogre 1.10 Mesh (.mesh)");



def register():
    bpy.utils.register_module(__name__);
    bpy.types.INFO_MT_file_import.append(menu_func_import_ogre_mesh);

def unregister():
    bpy.utils.unregister_module(__name__);
    bpy.types.INFO_MT_file_import.remove(menu_func_import_ogre_mesh);


if __name__ == "__main__":
    register();
