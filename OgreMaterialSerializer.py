from OgreSerializer import OgreSerializer
from enum import Enum
import re

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
        self usesVertexTextureFetch = False;
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
        self.lineNo = None;
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

    def _invokeParser(line, parsers):
        splitCmd = re.split(pattern=" |\t", string=line);

    def _parseScriptLine(self, line):
        if (self._scriptContext.section==OgreMaterialScriptSection.MSS_NONE):
            if (line=="}"):
                logParseError("Unexpected terminating brace.",self._scriptContext);
                return False;
            else:
                return _invokeParser(line,_rootAttribParsers);
