from enum import Enum
from io import open
import re
import sys

try:
    import bpy;
finally:
    print("You need to execute this script using blender");
    print("usage: blender --background --python OgreMaterialSerializer.py -- file.material");


try:
    from OgreSerializer import OgreSerializer
#For testing with blender
except ImportError as e:
    print("Import error: " + str(e) + " manual compilation" );
    filename="OgreSerializer.py";
    exec(compile(open(filename).read(), filename, 'exec'))



#Enumerates the types of programs which can run on the GPU.
class OgreGpuProgramType(Enum):
    GPT_VERTEX_PROGRAM = "GPT_VERTEX_PROGRAM";
    GPT_FRAGMENT_PROGRAM = "GPT_FRAGMENT_PROGRAM";
    GPT_GEOMETRY_PROGRAM = "GPT_GEOMETRY_PROGRAM";
    GPT_DOMAIN_PROGRAM = "GPT_DOMAIN_PROGRAM";
    GPT_HULL_PROGRAM = "GPT_HULL_PROGRAM";
    GPT_COMPUTE_PROGRAM = "GPT_COMPUTE_PROGRAM";

#Enum to identify material sections.
class OgreMaterialScriptSection(Enum):
    MSS_NONE = "MSS_NONE";
    MSS_MATERIAL = "MSS_MATERIAL";
    MSS_TECHNIQUE = "MSS_TECHNIQUE";
    MSS_PASS = "MSS_PASS";
    MSS_TEXTUREUNIT = "MSS_TEXTUREUNIT";
    MSS_PROGRAM_REF = "MSS_PROGRAM";
    MSS_PROGRAM = "MSS_PROGRAM";
    MSS_DEFAULT_PARAMETERS = "MSS_DEFAULT_PARAMETERS";
    MSS_TEXTURESOURCE = "MSS_TEXTURESOURCE";

#Struct for holding a program definition which is in progress.
class OgreMaterialScriptProgramDefinition:
    def __init__(self):
        self.name = "";
        self.progType = None;
        self.language = "";
        self.source = "";
        self.syntax = "";
        self.supportsSkeletalAnimation = False;
        self.supportsMorphAnimation = False;
        self.usesVertexTextureFetch = False;
        self.customParameters = {};

#Struct for holding the script context while parsing.Struct for holding the script context while parsing.
class OgreMaterialScriptContext:
    def __init__(self):
        self.section = OgreMaterialScriptSection.MSS_NONE;
        self.groupName = "";
        self.material = None;
        self.technique = None;
        self.Pass = None;
        self.textureUnit = None;
        self.program = None;
        self.isVertexProgramShadowCaster = False;
        self.isFragmentProgramShadowCaster = False;
        self.isVertexProgramShadowReceiver = False;
        self.isFragmentProgramShadowReceiver = False;
        self.programParams = None;
        self.numAnimationParametrics = 0;
        self.programDef = None;
        self.techLev = -1;
        self.passLev = -1;
        self.stateLev = -1;
        self.defaultParamLines = [];
        self.lineNo = 0;
        self.filename = "";


def logParseError(error, context):
    if (not context.filename and context.material is not None):
        print("Error in material " + context.material.name + " : " + error);
    else:
        if (context.material is not None):
            print("Error in material " + context.material.name + " at line " + str(context.lineNo) + " of " + context.filename + ": " + error);
        else:
            print("Error at line " + str(context.lineNo) + " of " + context.filename + ": " + error);


#function def for attribute parser; return value determines if the next line should be {
# bool attribute_parser(params_str, context)

def parseMaterial(params, context):
    vecparams = re.split(pattern=":",string=params,maxsplit=1);


    raise NotImplementedError;

def parseVertexProgram(params, context):
    raise NotImplementedError;

def parseGeometryProgram(params, context):
    raise NotImplementedError;

def parseFragmentProgram(params, context):
    raise NotImplementedError;

def parseTechnique(params, context):
    raise NotImplementedError;

def parsePass(params, context):
    raise NotImplementedError;

def parseAmbient(params, context):
    raise NotImplementedError;

def parseDiffuse(params, context):
    raise NotImplementedError;

def parseSpecular(params, context):
    raise NotImplementedError;

def parseEmissive(params, context):
    raise NotImplementedError;

def parseTextureUnit(params, context):
    raise NotImplementedError;

def parseTextureSource(params, context):
    raise NotImplementedError;

def parseTexture(params, context):
    raise NotImplementedError;

def parseTexCoord(params, context):
    raise NotImplementedError;

class OgreMaterialSerializer(OgreSerializer):


    def __init__(self):
        OgreSerializer.__init__(self);

        #Set up root attribute parsers
        self._rootAttribParsers = {};
        self._rootAttribParsers["material"] = parseMaterial;
        self._rootAttribParsers["vertex_program"] = parseVertexProgram;
        self._rootAttribParsers["geometry_program"] = parseGeometryProgram;
        self._rootAttribParsers["fragment_program"] = parseFragmentProgram;

        #Set up material attribute parsersSet up material attribute parsers
        self._materialAttribParsers = {};
        self._materialAttribParsers["technique"] = parseTechnique;

        #Set up technique attribute parsersSet up technique attribute parsers
        self._techniqueAttribParsers = {};
        self._techniqueAttribParsers["pass"] = parsePass;

        #Set up pass attribute parsersSet up pass attribute parsers
        self._passAttribParsers = {};
        self._passAttribParsers["ambient"] = parseAmbient;
        self._passAttribParsers["diffuse"] = parseDiffuse;
        self._passAttribParsers["specular"] = parseSpecular;
        self._passAttribParsers["emissive"] = parseEmissive;
        self._passAttribParsers["texture_unit"] = parseTextureUnit;

        #Set up texture unit attribute parsers
        self._textureUnitAttribParsers = {};
        self._textureUnitAttribParsers["texture_source"] = parseTextureSource;
        self._textureUnitAttribParsers["texture"] = parseTexture;
        self._textureUnitAttribParsers["tex_coord_set"] = parseTexCoord;

        #Set up program reference attribute parsers
        self._programRefAttribParsers = {};

        #Set up program definition attribute parsers
        self._programAttribParsers = {};

        #Set up program default param attribute parsersSet up program default param attribute parsers
        self._programDefaultParamAttribParsers = {};

        self._scriptContext = OgreMaterialScriptContext();
        self._defaults = False;

    def _invokeParser(self,line, parsers):
        splitCmd = re.split(pattern=" |\t", string=line, maxsplit=1);
        if (splitCmd[0] in parsers):
            cmd = "";
            if (len(splitCmd) >= 2):
                cmd = splitCmd[1];
            return parsers[splitCmd[0]](cmd,self._scriptContext);
        else:
            logParseError("Unrecognised command: " + splitCmd[0], self._scriptContext);
            return False;


    def _parseScriptLine(self, line):
        section = self._scriptContext.section;
        if (section==OgreMaterialScriptSection.MSS_NONE):
            if (line=="}"):
                logParseError("Unexpected terminating brace.",self._scriptContext);
                return False;
            else:
                return self._invokeParser(line,self._rootAttribParsers);
        elif (section==OgreMaterialScriptSection.MSS_MATERIAL):
            if (line=="}"):
                self._scriptContext.section = OgreMaterialScriptSection.MSS_NONE;
                self._scriptContext.material = None;
                self._scriptContext.passLev = -1;
                self._scriptContext.stateLev = -1;
                self._scriptContext.techLev = -1;
            else:
                return self._invokeParser(line,self._materialAttribParsers);
        elif (section==OgreMaterialScriptSection.MSS_TECHNIQUE):
            if (line=="}"):
                self._scriptContext.section = OgreMaterialScriptSection.MSS_MATERIAL;
                self._scriptContext.passLev = -1;
            else:
                return self._invokeParser(line,self._techniqueAttribParsers);
        elif (section==OgreMaterialScriptSection.MSS_PASS):
            if (line=="}"):
                self._scriptContext.section = OgreMaterialScriptSection.MSS_TECHNIQUE;
                self._scriptContext.Pass = None;
                self._scriptContext.stateLev = -1;
            else:
                return self._invokeParser(line, self._passAttribParsers);
        elif (section==OgreMaterialScriptSection.MSS_TEXTUREUNIT):
            if (line=="}"):
                self._scriptContext.section = OgreMaterialScriptSection.MSS_PASS;
                self._scriptContext.textureUnit = None;
            else:
                return self._invokeParser(line,self._textureUnitAttribParsers);
        elif (section==OgreMaterialScriptSection.MSS_TEXTURESOURCE):
            if (line=="}"):
                #TODO END CREATING TEXTURE
                self._scriptContext.section = OgreMaterialScriptSection.MSS_TEXTUREUNIT;
            else:
                #TODO PARSE TEXTURE CUSTOM PARAMETERS
                pass;
        elif (section==OgreMaterialScriptSection.MSS_PROGRAM_REF):
            if (line=="}"):
                self._scriptContext.section = OgreMaterialScriptSection.MSS_PASS;
                self._scriptContext.program = None;
            else:
                return self._invokeParser(line,self._programRefAttribParsers);
        elif (section==OgreMaterialScriptSection.MSS_PROGRAM):
            if (line=="}"):
                #TODO FINNISH PROGRAM definition
                self._scriptContext.section = OgreMaterialScriptSection.MSS_NONE;
                self._scriptContext.defaultParamLines = [];
                self._scriptContext.programDef = None;
            else:
                #TODO FIND AND INVOKE A custom parser
                return self._invokeParser(line, self._programAttribParsers);
        elif (section==OgreMaterialScriptContext.MSS_DEFAULT_PARAMETERS):
            if (lines=="}"):
                self._scriptContext.section = OgreMaterialScriptSection.MSS_PROGRAM;
            else:
                self._scriptContext.defaultParamLines.append(line);
        return False;

    def parseScript(self,stream, filename="", groupName="GLOBAL"):
        self._scriptContext = OgreMaterialScriptContext();
        self._scriptContext.filename = filename;
        self._scriptContext.groupName = groupName;
        eof = False;
        nextIsOpenBracket = False;
        while (not eof):
            try:
                line = self._readString(stream);
                self._scriptContext.lineNo += 1;
                if (not ((not line) or line.startswith("//"))):
                    if (nextIsOpenBracket):
                        if (line != "{"):
                            logParseError("Expecting '{' but got " + line + " instead.", self._scriptContext);
                        nextIsOpenBracket = False;
                    else:
                        nextIsOpenBracket = self._parseScriptLine(line);

            except EOFError as e:
                eof = True;
        if (self._scriptContext.section != OgreMaterialScriptSection.MSS_NONE):
            logParseError("Unexpected end of file.", self._scriptContext);


#use the following cmdline for test with blender
#"blender --background --python OgreMaterialSerializer.py -- OgreMaterialSerializer.py filname.material"

#if __name__ == "__main__":
#    argv = sys.argv;
#    argv = argv[argv.index("--")+1:];  # get all args after "--"
#    if (len(argv) > 1):
#        filename = argv[1];
#        matfile = open(filename,mode='rb');
#        matserializer = OgreMaterialSerializer();
#        matserializer.disableValidation();
#        matserializer.parseScript(matfile, filename);
#    else:
#        print("usage: python " + argv[0] + " file.material");
#

if __name__ == "__main__":
    argv = sys.argv;
    argv = argv[argv.index("--")+1:];  # get all args after "--"
    if (len(argv) > 0):
        filename = argv[0];
        matfile = open(filename,mode='rb');
        matserializer = OgreMaterialSerializer();
        matserializer.disableValidation();
        matserializer.parseScript(matfile, filename);
    else:
        print("usage: blender --background --python OgreMaterialSerializer.py -- file.material");
