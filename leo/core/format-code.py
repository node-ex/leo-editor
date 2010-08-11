#@+leo-ver=5-thin
#@+node:ekr.20100811091636.5997: * @thin format-code.py
#@+others
#@+node:ekr.20100811091636.5838: ** @button format-code
'''A script showing how to convert code in Leo outlines to rST/Sphinx code.

The defaultOptions dict specifies default options.'''


#@+<< imports >>
#@+node:ekr.20100811091636.5919: *3* << imports >>
import leo.core.leoGlobals as g
import leo.core.leoTest as leoTest
import leo.core.leoCommands as commands

import os
import pprint

if g.isPython3:
    import io
    StringIO = io.StringIO
else:
    import StringIO
    StringIO = StringIO.StringIO

import sys

#@-<< imports >>
#@+<< define defaultOptionsDict >>
#@+node:ekr.20100811091636.5995: *3* << define defaultOptionsDict >>
# fn = 'format-code.rst.txt' # 
fn = '%s.rst.txt' % (g.sanitize_filename(p.h))

options = {
    'output-file-name': fn,
    'verbose',True
}
#@-<< define defaultOptionsDict >>

class formatController:

    '''A class to convert a Leo outline to rst/Sphinx markup.
    The outline is presumed to contain computer source code.'''

    #@+others
    #@+node:ekr.20100811091636.5996: *3* Unused
    if 0:
        #@+others
        #@+node:ekr.20100811091636.5957: *4* writeToDocutils (sets argv) & helper
        def writeToDocutils (self,s):

            '''Send s to docutils using the writer implied by self.ext and return the result.'''

            trace = False and not g.unitTesting

            if not docutils:
                g.es('docutils not present',color='red')
                return

            openDirectory = self.c.frame.openDirectory
            overrides = {'output_encoding': self.encoding }

            # Compute the args list if the stylesheet path does not exist.
            styleSheetArgsDict = self.handleMissingStyleSheetArgs()

            for ext,writer in (
                ('.html','html'),
                ('.htm','html'),
                ('.tex','latex'),
                ('.pdf','leo_pdf'),
            ):
                if self.ext == ext:
                    break
            else:
                g.es_print('unknown docutils extension: %s' % (self.ext),color='red')
                return ''

            # Make the stylesheet path relative to the directory containing the output file.
            rel_stylesheet_path = self.getOption('stylesheet_path') or ''

            # New in Leo 4.5: The rel_stylesheet_path is relative to the open directory.
            stylesheet_path = g.os_path_finalize_join(
                self.c.frame.openDirectory,rel_stylesheet_path)

            path = g.os_path_finalize_join(
                stylesheet_path,self.getOption('stylesheet_name'))

            res = ""
            if self.getOption('stylesheet_embed') == False:
                rel_path = g.os_path_join(
                    rel_stylesheet_path,self.getOption('stylesheet_name'))
                rel_path = rel_path.replace('\\','/') # 2010/01/28
                overrides['stylesheet'] = rel_path
                overrides['stylesheet_path'] = None
                overrides['embed_stylesheet'] = None
            elif g.os_path_exists(path):
                if self.ext != '.pdf':
                    overrides['stylesheet'] = path
                    overrides['stylesheet_path'] = None
            elif styleSheetArgsDict:
                g.es_print('using publish_argv_for_missing_stylesheets',
                    styleSheetArgsDict)
                overrides.update(styleSheetArgsDict)
                    # MWC add args to settings
            elif rel_stylesheet_path == stylesheet_path:
                g.es_print('stylesheet not found: %s' % (path),color='red')
            else:
                g.es_print('stylesheet not found\n',path,color='red')
                if self.path:g.es_print('@path:', self.path)
                g.es_print('open path:',self.c.frame.openDirectory)
                if rel_stylesheet_path:
                    g.es_print('relative path:', rel_stylesheet_path)
            try:
                # All paths now come through here.
                if trace: g.trace('overrides',overrides)
                result = None # Ensure that result is defined.
                result = docutils.core.publish_string(source=s,
                        reader_name='standalone',
                        parser_name='restructuredtext',
                        writer_name=writer,
                        settings_overrides=overrides)
            except docutils.ApplicationError as error:
                # g.es_print('Docutils error (%s):' % (
                    # error.__class__.__name__),color='red')
                g.es_print('Docutils error:',color='red')
                g.es_print(error,color='blue')
            except Exception:
                g.es_print('Unexpected docutils exception')
                g.es_exception()
            return result
        #@+node:ekr.20100811091636.5958: *5* handleMissingStyleSheetArgs
        def handleMissingStyleSheetArgs (self,s=None):

            '''Parse the publish_argv_for_missing_stylesheets option,
            returning a dict containing the parsed args.'''

            force = False
            if force:
                # See http://docutils.sourceforge.net/docs/user/config.html#documentclass
                return {'documentclass':'report', 'documentoptions':'english,12pt,lettersize'}

            if not s:
                s = self.getOption('publish_argv_for_missing_stylesheets')
            if not s: return {}

            # Handle argument lists such as this:
            # --language=en,--documentclass=report,--documentoptions=[english,12pt,lettersize]
            d = {}
            while s:
                s = s.strip()
                if not s.startswith('--'): break
                s = s[2:].strip()
                eq = s.find('=')
                cm = s.find(',')
                if eq == -1 or (-1 < cm < eq): # key[nl] or key,
                    val = ''
                    cm = s.find(',')
                    if cm == -1:
                        key = s.strip()
                        s = ''
                    else:
                        key = s[:cm].strip()
                        s = s[cm+1:].strip()
                else: # key = val
                    key = s[:eq].strip()
                    s = s[eq+1:].strip()
                    if s.startswith('['): # [...]
                        rb = s.find(']')
                        if rb == -1: break # Bad argument.
                        val = s[:rb+1]
                        s = s[rb+1:].strip()
                        if s.startswith(','):
                            s = s[1:].strip()
                    else: # val[nl] or val,
                        cm = s.find(',')
                        if cm == -1:
                            val = s
                            s = ''
                        else:
                            val = s[:cm].strip()
                            s = s[cm+1:].strip()

                # g.trace('key',repr(key),'val',repr(val),'s',repr(s))
                if not key: break
                if not val.strip(): val = '1'
                d[str(key)] = str(val)

            return d
        #@+node:ekr.20100811091636.5932: *4* createDefaultOptionsDict
        def createDefaultOptionsDict(self):

            # Warning: changing the names of options changes the names of the corresponding ivars.

            self.defaultOptionsDict = {
                # Http options...
                'rst3_clear_http_attributes':   False,
                'rst3_http_server_support':     False,
                'rst3_http_attributename':      'rst_http_attribute',
                'rst3_node_begin_marker':       'http-node-marker-',
                # Path options...
                'rst3_default_path': None, # New in Leo 4.4a4 # Bug fix: must be None, not ''.
                'rst3_stylesheet_name': 'default.css',
                'rst3_stylesheet_path': None, # Bug fix: must be None, not ''.
                    'rst3_stylesheet_embed': True,
                'rst3_publish_argv_for_missing_stylesheets': None,
                # Global options...
                'rst3_call_docutils': True, # 2010/08/05
                'rst3_code_block_string': '',
                'rst3_number_code_lines': True,
                'rst3_underline_characters': '''#=+*^~"'`-:><_''',
                'rst3_verbose':True,
                'rst3_write_intermediate_file': False, # Used only if generate_rst is True.
                'rst3_write_intermediate_extension': 'txt',
                # Mode options...
                'rst3_code_mode': False, # True: generate rst markup from @code and @doc parts.
                'rst3_doc_only_mode': False, # True: generate only from @doc parts.
                'rst3_generate_rst': True, # True: generate rst markup.  False: generate plain text.
                'rst3_generate_rst_header_comment': True,
                    # True generate header comment (requires generate_rst option)
                # Formatting options that apply to both code and rst modes....
                'rst3_show_headlines': True,  # Can be set by @rst-no-head headlines.
                'rst3_show_organizer_nodes': True,
                'rst3_show_options_nodes': False,
                'rst3_show_sections': True,
                'rst3_strip_at_file_prefixes': True,
                'rst3_show_doc_parts_in_rst_mode': True,
                # Formatting options that apply only to code mode.
                'rst3_show_doc_parts_as_paragraphs': False,
                'rst3_show_leo_directives': True,
                'rst3_show_markup_doc_parts': False,
                'rst3_show_options_doc_parts': False,
                # *Names* of headline commands...
                'rst3_code_prefix':             '@rst-code',     # Enter code mode.
                'rst3_doc_only_prefix':         '@rst-doc-only', # Enter doc-only mode.
                'rst3_rst_prefix':              '@rst-rst',     # Enter rst mode.
                'rst3_ignore_headline_prefix':  '@rst-no-head',
                'rst3_ignore_headlines_prefix': '@rst-no-headlines',
                'rst3_ignore_node_prefix':      '@rst-ignore-node',
                'rst3_ignore_prefix':           '@rst-ignore',
                'rst3_ignore_tree_prefix':      '@rst-ignore-tree',
                'rst3_option_prefix':           '@rst-option',
                'rst3_options_prefix':          '@rst-options',
                'rst3_preformat_prefix':        '@rst-preformat',
                'rst3_show_headline_prefix':    '@rst-head',
            }
        #@+node:ekr.20100811091636.5935: *4* initCodeBlockString
        def initCodeBlockString(self,p):

            # New in Leo 4.4.4: do this here, not in initWrite.
            trace = False and not g.unitTesting
            c = self.c
            # if trace: os.system('cls')
            d = c.scanAllDirectives(p)
            language = d.get('language')
            if language is None: language = 'python'
            else: language = language.lower()
            syntax = SilverCity is not None

            if trace: g.trace('language',language,'language.title()',language.title(),p.h)

            # Note: lines that end with '\n\n' are a signal to handleCodeMode.
            s = self.getOption('code_block_string')
            if s:
                self.code_block_string = s.replace('\\n','\n')
            elif syntax and language in ('python','ruby','perl','c'):
                self.code_block_string = '**code**:\n\n.. code-block:: %s\n\n' % (
                    language.title())
            else:
                self.code_block_string = '**code**:\n\n.. class:: code\n..\n\n::\n\n'
        #@+node:ekr.20100811091636.5929: *4* munge
        def munge (self,name):

            '''Convert an option name to the equivalent ivar name.'''

            i = g.choose(name.startswith('rst'),3,0)

            while i < len(name) and name[i].isdigit():
                i += 1

            if i < len(name) and name[i] == '_':
                i += 1

            s = name[i:].lower()
            s = s.replace('-','_')

            return s
        #@+node:ekr.20100811091636.5948: *4* Top-level write code
        #@+node:ekr.20100811091636.5954: *5* processTopTree
        def processTopTree (self,p,justOneFile=False):

            c = self.c ; current = p.copy()

            for p in current.self_and_parents():
                h = p.h
                if h.startswith('@rst') and not h.startswith('@rst-'):
                    self.processTree(p,ext=None,toString=False,justOneFile=justOneFile)
                    break
            else:
                self.processTree(current,ext=None,toString=False,justOneFile=justOneFile)

            g.es_print('done',color='blue')
        #@+node:ekr.20100811091636.5955: *5* processTree
        def processTree(self,p,ext,toString,justOneFile):

            '''Process all @rst nodes in a tree.'''

            self.preprocessTree(p)
            found = False ; self.stringOutput = ''
            p = p.copy() ; after= p.nodeAfterTree()
            while p and p != after:
                h = p.h.strip()
                if g.match_word(h,0,"@rst"):
                    self.outputFileName = h[4:].strip()
                    if (
                        (self.outputFileName and self.outputFileName[0] != '-') or
                        (toString and not self.outputFileName)
                    ):
                        found = True
                        self.topLevel = p.level() # Define toplevel separately for each rst file.
                        if toString:
                            self.ext = ext
                            if not self.ext.startswith('.'):
                                self.ext = '.'+self.ext
                        else:
                            self.ext = g.os_path_splitext(self.outputFileName)[1].lower()
                        # g.trace('ext',self.ext,self.outputFileName)
                        if self.ext in ('.htm','.html','.tex','.pdf'):
                            ok = self.writeSpecialTree(p,toString=toString,justOneFile=justOneFile)
                        else:
                            ok = self.writeNormalTree(p,toString=toString)
                        self.scanAllOptions(p) # Restore the top-level verbose setting.
                        if toString:
                            return p.copy(),self.stringOutput
                        else:
                            if ok: self.report(self.outputFileName)
                        p.moveToNodeAfterTree()
                    else:
                        p.moveToThreadNext()
                else: p.moveToThreadNext()
            if not found:
                g.es('No @rst nodes in selected tree',color='blue')
            return None,None
        #@+node:ekr.20100811091636.5950: *5* writeAtAutoFile
        def writeAtAutoFile (self,p,fileName,outputFile,trialWrite=False):

            '''Write an @auto tree containing imported rST code.
            The caller will close the output file.'''

            # g.trace('trial',trialWrite,fileName,outputFile)

            try:
                self.trialWrite = trialWrite
                self.atAutoWrite = True
                self.initAtAutoWrite(p,fileName,outputFile)
                self.topNode = p.copy() # Indicate the top of this tree.
                self.topLevel = p.level()
                after = p.nodeAfterTree()
                ok = self.isSafeWrite(p)
                if ok:
                    p = p.firstChild() # A hack: ignore the root node.
                    while p and p != after:
                        self.writeNode(p) # side effect: advances p
            finally:
                self.atAutoWrite = False
            return ok
        #@+node:ekr.20100811091636.5951: *6* initAtAutoWrite (rstCommands)
        def initAtAutoWrite(self,p,fileName,outputFile):

            # Set up for a standard write.
            self.createDefaultOptionsDict()
            self.vnodeOptionDict = {}
            self.scanAllOptions(p)
            self.initWrite(p)
            self.preprocessTree(p) # Allow @ @rst-options, for example.
            # Do the overrides.
            self.outputFile = outputFile
            self.outputFileName = fileName
            # Set underlining characters.
            # It makes no sense to use user-defined
            # underlining characters in @auto-rst.
            d = p.v.u.get('rst-import',{})
            underlines2 = d.get('underlines2','')
                # Do *not* set a default for overlining characters.
            if len(underlines2) > 1:
                underlines2 = underlines2[0]
                g.trace('too many top-level underlines, using %s' % (
                    underlines2),color='blue')
            underlines1 = d.get('underlines1','')
            # Bug fix:  2010/05/26: pad underlines with default characters.
            default_underlines = '=+*^~"\'`-:><_'
            if underlines1:
                for ch in default_underlines[1:]:
                    if ch not in underlines1:
                        underlines1 = underlines1 + ch
            else:
                underlines1 = default_underlines
            self.atAutoWriteUnderlines   = underlines2 + underlines1
            self.underlines1 = underlines1
            self.underlines2 = underlines2
        #@+node:ekr.20100811091636.5952: *6* isSafeWrite
        def isSafeWrite (self,p):

            '''Return True if node p contributes nothing but
            rst-options to the write.'''

            if self.trialWrite or not p.isAtAutoRstNode():
                return True # Trial writes are always safe.

            lines = g.splitLines(p.b)
            for z in lines:
                if z.strip() and not z.startswith('@') and not z.startswith('.. '):
                    # A real line that will not be written.
                    g.es('unsafe @auto-rst',color='red')
                    g.es('body text will be ignored in\n',p.h)
                    return False
            else:
                return True
        #@+node:ekr.20100811091636.5959: *5* writeNodeToString (New in 4.4.1)
        def writeNodeToString (self,p=None,ext=None):

            '''Scan p's tree (defaults to presently selected tree) looking for @rst nodes.
            Convert the first node found to an ouput of the type specified by ext.

            The @rst may or may not be followed by a filename; the filename is *ignored*,
            and its type does not affect ext or the output generated in any way.

            ext should start with a period: .html, .tex or None (specifies rst output).

            Returns p, s, where p is the position of the @rst node and s is the converted text.'''

            c = self.c ; current = p or c.p

            for p in current.self_and_parents():
                if p.h.startswith('@rst'):
                    return self.processTree(p,ext=ext,toString=True,justOneFile=True)
            else:
                return self.processTree(current,ext=ext,toString=True,justOneFile=True)
        #@+node:ekr.20100811091636.5953: *5* writeNormalTree
        def writeNormalTree (self,p,toString=False):

            self.initWrite(p)

            # Always write to a string first.
            self.outputFile = StringIO()
            self.writeTree(p)
            self.source = self.stringOutput = self.outputFile.getvalue()

            # Copy to a file if requested.
            if not toString:
                # Comput the output file name *after* calling writeTree.
                self.outputFileName = self.computeOutputFileName(self.outputFileName)
                self.outputFile = open(self.outputFileName,'w')
                self.outputFile.write(self.stringOutput)
                self.outputFile.close()

            return True
        #@+node:ekr.20100811091636.5956: *5* writeSpecialTree
        def writeSpecialTree (self,p,toString,justOneFile):

            c = self.c
            isHtml = self.ext in ('.html','.htm')
            if isHtml and not SilverCity:
                if not self.silverCityWarningGiven:
                    self.silverCityWarningGiven = True
                    g.es('SilverCity not present so no syntax highlighting')

            self.initWrite(p)
                # was encoding=g.choose(isHtml,'utf-8','iso-8859-1'))
            self.outputFile = StringIO()
            self.writeTree(p)
            self.source = self.outputFile.getvalue()
            self.outputFile = None

            if not toString:
                # Compute this here for use by intermediate file.
                self.outputFileName = self.computeOutputFileName(self.outputFileName)

                # Create the directory if it doesn't exist.
                theDir, junk = g.os_path_split(self.outputFileName)
                theDir = c.os_path_finalize(theDir)
                if not g.os_path_exists(theDir):
                    ok = g.makeAllNonExistentDirectories(theDir,c=c,force=False)
                    if not ok:
                        g.es_print('did not create:',theDir,color='red')
                        return False

                if self.getOption('write_intermediate_file'):
                    ext = self.getOption('write_intermediate_extension')
                    name = self.outputFileName.rsplit('.',1)[0] + ext 
                    if g.isPython3: # 2010/04/21
                        f = open(name,'w',encoding=self.encoding)
                    else:
                        f = open(name,'w')
                    f.write(self.source)
                    f.close()
                    self.report(name)

            # g.trace('call_docutils',self.getOption('call_docutils'))
            if not self.getOption('call_docutils'):
                return False

            try:
                output = self.writeToDocutils(self.source)
                ok = output is not None
            except Exception:
                g.pr('Exception in docutils')
                g.es_exception()
                ok = False

            if ok:
                if isHtml:
                    import re
                    # g.trace(repr(output)) # Type is byte for Python3.
                    if g.isBytes(output):
                        output = g.toUnicode(output)
                    idxTitle = output.find('<title></title>')
                    if idxTitle > -1:
                        m = re.search('<h1>([^<]*)</h1>', output)
                        if not m:
                            m = re.search('<h1><[^>]+>([^<]*)</a></h1>', output)
                        if m:
                            output = output.replace(
                                '<title></title>',
                                '<title>%s</title>' % m.group(1)
                            )

                if toString:
                    self.stringOutput = output
                else:
                    # Write the file to the directory containing the .leo file.
                    f = open(self.outputFileName,'w')
                    f.write(output)
                    f.close()
                    self.http_endTree(self.outputFileName, p, justOneFile=justOneFile)

            return ok
        #@+node:ekr.20100811091636.5983: *4* computeOutputFileName
        def computeOutputFileName (self,fileName):

            openDirectory = self.c.frame.openDirectory
            default_path = self.getOption('default_path')

            if default_path:
                path = g.os_path_finalize_join(self.path,default_path,fileName)
            elif self.path:
                path = g.os_path_finalize_join(self.path,fileName)
            elif openDirectory:
                path = g.os_path_finalize_join(self.path,openDirectory,fileName)
            else:
                path = g.os_path_finalize_join(fileName)

            # g.trace('openDirectory %s\ndefault_path %s\npath %s' % (
                # repr(openDirectory),repr(default_path),repr(path)))

            return path
        #@-others
    #@+node:ekr.20100811091636.5921: *3* class formatter
    class formatter:

        '''A class to convert a Leo outline containing computer source code to rst/Sphinx markup.'''

        #@+others
        #@+node:ekr.20100811091636.5922: *4*  Birth & init
        #@+node:ekr.20100811091636.5923: *5*  ctor (rstClass)
        def __init__ (self,c,defaultOptionsDict):

            global SilverCity

            self.c = c
            #@+<< init ivars >>
            #@+node:ekr.20100811091636.5924: *6* << init ivars >> (leoRst)
            self.silverCityWarningGiven = False

            # The options dictionary.
            self.optionsDict = {}
            self.option_prefix = '@rst-option'

            # Formatting...
            self.code_block_string = ''
            self.node_counter = 0
            self.topLevel = 0
            self.topNode = None
            self.use_alternate_code_block = SilverCity is None

            # Http support...
            self.nodeNumber = 0
            # All nodes are numbered so that unique anchors can be generated.

            self.http_map = {} 
            # Keys are named hyperlink targets.  Value are positions.
            # The targets mark the beginning of the html code specific
            # for this position.

            self.anchor_map = {}
            # Maps anchors (generated by this module) to positions

            self.rst3_all = False
            # Set to True by the button which processes all @rst trees.

            # For writing.
            self.atAutoWrite = False # True, special cases for writeAtAutoFile.
            self.atAutoWriteUnderlines = '' # Forced underlines for writeAtAutoFile.
            self.leoDirectivesList = g.globalDirectiveList
            self.encoding = 'utf-8'
            self.ext = None # The file extension.
            self.outputFileName = None # The name of the file being written.
            self.outputFile = None # The open file being written.
            self.path = '' # The path from any @path directive.
            self.source = None # The written source as a string.
            self.trialWrite = False # True if doing a trialWrite.
            #@-<< init ivars >>
            ### self.createDefaultOptionsDict()
            self.defaultOptionsDict = defaultOptionsDict
            self.initOptionsFromSettings() # Still needed.
            self.initHeadlineCommands() # Only needs to be done once.
            self.initSingleNodeOptions()
        #@+node:ekr.20100811091636.5926: *5* finishCreate
        def finishCreate(self):

            c = self.c
            d = self.getPublicCommands()
            c.commandsDict.update(d)
        #@+node:ekr.20100811091636.5927: *5* initHeadlineCommands
        def initHeadlineCommands (self):

            '''Init the list of headline commands used by writeHeadline.'''

            self.headlineCommands = [
                self.getOption('code_prefix'),
                self.getOption('doc_only_prefix'),
                self.getOption('default_path_prefix'),
                self.getOption('rst_prefix'),
                self.getOption('ignore_headline_prefix'),
                self.getOption('ignore_headlines_prefix'),
                self.getOption('ignore_node_prefix'),
                self.getOption('ignore_tree_prefix'),
                self.getOption('option_prefix'),
                self.getOption('options_prefix'),
                self.getOption('show_headline_prefix'),
                # # Suggested by Hemanth P.S.: prevent @file nodes from creating headings.
                # self.getOption('keep_at_file_prefix'),
                # self.getOption('strip_at_file_prefix'),
            ]
        #@+node:ekr.20100811091636.5928: *5* initSingleNodeOptions
        def initSingleNodeOptions (self):

            self.singleNodeOptions = [
                'ignore_this_headline',
                'ignore_this_node',
                'ignore_this_tree',
                'preformat_this_node',
                'show_this_headline',
            ]
        #@+node:ekr.20100811091636.5930: *4* run & top-level code
        def run (self,event=None):

            # self.processTopTree(self.c.p)

            # self.processTree(self.c.p) ### ,ext=None,toString=False,justOneFile=justOneFile)

            # self.writeSpecialTree(p,toString=toString,justOneFile=justOneFile)

            self.outputFile = StringIO()
            self.writeTree(p)
            s = self.outputFile.getvalue()
            fn = self.defaultOptionsDict.get('output-file-name','format-code.rst.txt')
            self.outputFile = open(self.outputFileName,'w')
            self.outputFile.write(s)
            self.outputFile.close()
        #@+node:ekr.20100811091636.5949: *5* initWrite
        def initWrite (self,p):

            self.initOptionsFromSettings() # Still needed.

            # Set the encoding from any parent @encoding directive.
            # This can be overridden by @rst-option encoding=whatever.
            c = self.c
            d = c.scanAllDirectives(p)
            self.encoding = d.get('encoding') or 'utf-8'
            self.path = d.get('path') or ''

            # g.trace('path:',self.path)
        #@+node:ekr.20100811091636.5931: *4* options...
        #@+node:ekr.20100811091636.5933: *5* dumpSettings (debugging)
        def dumpSettings (self):

            d = self.optionsDict
            keys = sorted(d)

            g.pr('present settings...')
            for key in keys:
                g.pr('%20s %s' % (key,d.get(key)))
        #@+node:ekr.20100811091636.5934: *5* getOption
        def getOption (self,name):

            return self.optionsDict.get(name)
        #@+node:ekr.20100811091636.5936: *5* preprocessTree & helpers
        def preprocessTree (self,root):

            self.vnodeOptionDict = {}

            # Bug fix 12/4/05: must preprocess parents too.
            for p in root.parents():
                self.preprocessNode(p)

            for p in root.self_and_subtree():
                self.preprocessNode(p)

            if 0:
                g.trace(root.h)
                for key in self.vnodeOptionDict.keys():
                    g.trace(key)
                    g.printDict(self.tnodeOptionDict.get(key))
        #@+node:ekr.20100811091636.5937: *6* preprocessNode
        def preprocessNode (self,p):

            d = self.vnodeOptionDict.get(p.v)
            if d is None:
                d = self.scanNodeForOptions(p)
                self.vnodeOptionDict [p.v] = d
        #@+node:ekr.20100811091636.5938: *6* parseOptionLine
        def parseOptionLine (self,s):

            '''Parse a line containing name=val and return (name,value) or None.

            If no value is found, default to True.'''

            s = s.strip()
            if s.endswith(','): s = s[:-1]
            # Get name.  Names may contain '-' and '_'.
            i = g.skip_id(s,0,chars='-_')
            name = s [:i]
            if not name: return None
            j = g.skip_ws(s,i)
            if g.match(s,j,'='):
                val = s [j+1:].strip()
                # g.trace(val)
                return name,val
            else:
                # g.trace('*True')
                return name,'True'
        #@+node:ekr.20100811091636.5939: *6* scanForOptionDocParts
        def scanForOptionDocParts (self,p,s):

            '''Return a dictionary containing all options from @rst-options doc parts in p.
            Multiple @rst-options doc parts are allowed: this code aggregates all options.
            '''

            d = {} ; n = 0 ; lines = g.splitLines(s)
            while n < len(lines):
                line = lines[n] ; n += 1
                if line.startswith('@'):
                    i = g.skip_ws(line,1)
                    for kind in ('@rst-options','@rst-option'):
                        if g.match_word(line,i,kind):
                            # Allow options on the same line.
                            line = line[i+len(kind):]
                            d.update(self.scanOption(p,line))
                            # Add options until the end of the doc part.
                            while n < len(lines):
                                line = lines[n] ; n += 1 ; found = False
                                for stop in ('@c','@code', '@'):
                                    if g.match_word(line,0,stop):
                                        found = True ; break
                                if found:
                                    break
                                else:
                                    d.update(self.scanOption(p,line))
                            break
            return d
        #@+node:ekr.20100811091636.5940: *6* scanHeadlineForOptions
        def scanHeadlineForOptions (self,p):

            '''Return a dictionary containing the options implied by p's headline.'''

            h = p.h.strip()

            if p == self.topNode:
                return {} # Don't mess with the root node.
            elif g.match_word(h,0,self.getOption('option_prefix')): # '@rst-option'
                s = h [len(self.option_prefix):]
                return self.scanOption(p,s)
            elif g.match_word(h,0,self.getOption('options_prefix')): # '@rst-options'
                return self.scanOptions(p,p.b)
            else:
                # Careful: can't use g.match_word because options may have '-' chars.
                i = g.skip_id(h,0,chars='@-')
                word = h[0:i]

                for prefix,ivar,val in (
                    ('code_prefix','code_mode',True), # '@rst-code'
                    ('doc_mode_prefix','doc_only_mode',True), # @rst-doc-only.
                    ('default_path_prefix','default_prefix',''), # '@rst-default-path'
                    ('rst_prefix','code_mode',False), # '@rst'
                    ('ignore_headline_prefix','ignore_this_headline',True), # '@rst-no-head'
                    ('show_headline_prefix','show_this_headline',True), # '@rst-head'  
                    ('ignore_headlines_prefix','show_headlines',False), # '@rst-no-headlines'
                    ('ignore_prefix','ignore_this_tree',True),      # '@rst-ignore'
                    ('ignore_node_prefix','ignore_this_node',True), # '@rst-ignore-node'
                    ('ignore_tree_prefix','ignore_this_tree',True), # '@rst-ignore-tree'
                    ('preformat_prefix','preformat_this_node',True), # '@rst-preformat
                ):
                    prefix = self.getOption(prefix)
                    if prefix and word == prefix: # Do _not_ munge this prefix!
                        d = { ivar: val }
                        if ivar != 'code_mode':
                            d ['code_mode'] = False # Enter rst mode.
                            d ['doc_only_mode'] = False
                        # Special case: Treat a bare @rst like @rst-no-head
                        if h == self.getOption('rst_prefix'):
                            d ['ignore_this_headline'] = True
                        # g.trace(repr(h),repr(prefix),ivar,d)
                        return d

                if h.startswith('@rst'):
                    g.trace('word',word,'rst_prefix',self.getOption('rst_prefix'))
                    g.trace('unknown kind of @rst headline',p.h)

                return {}
        #@+node:ekr.20100811091636.5941: *6* scanNodeForOptions
        def scanNodeForOptions (self,p):

            '''Return a dictionary containing all the option-name:value entries in p.

            Such entries may arise from @rst-option or @rst-options in the headline,
            or from @ @rst-options doc parts.'''

            h = p.h

            d = self.scanHeadlineForOptions(p)

            d2 = self.scanForOptionDocParts(p,p.b)

            # A fine point: body options over-ride headline options.
            d.update(d2)

            return d
        #@+node:ekr.20100811091636.5942: *6* scanOption
        def scanOption (self,p,s):

            '''Return { name:val } if s is a line of the form name=val.
            Otherwise return {}'''

            if not s.strip() or s.strip().startswith('..'): return {}

            data = self.parseOptionLine(s)

            if data:
                name,val = data
                fullName = 'rst3_' + self.munge(name)
                if fullName in list(self.defaultOptionsDict.keys()):
                    if   val.lower() == 'true': val = True
                    elif val.lower() == 'false': val = False
                    # g.trace('%24s %8s %s' % (self.munge(name),val,p.h))
                    return { self.munge(name): val }
                else:
                    g.es_print('ignoring unknown option: %s' % (name),color='red')
                    return {}
            else:
                g.trace(repr(s))
                s2 = 'bad rst3 option in %s: %s' % (p.h,s)
                g.es_print(s2,color='red')
                return {}
        #@+node:ekr.20100811091636.5943: *6* scanOptions
        def scanOptions (self,p,s):

            '''Return a dictionary containing all the options in s.'''

            d = {}

            for line in g.splitLines(s):
                d2 = self.scanOption(p,line)
                if d2: d.update(d2)

            return d
        #@+node:ekr.20100811091636.5944: *5* scanAllOptions & helpers
        # Once an option is seen, no other related options in ancestor nodes have any effect.

        def scanAllOptions(self,p):

            '''Scan position p and p's ancestors looking for options,
            setting corresponding ivars.
            '''

            self.initOptionsFromSettings() # Must be done on every node.
            self.handleSingleNodeOptions(p)
            seen = self.singleNodeOptions[:] # Suppress inheritance of single-node options.

            # g.trace('-'*20)
            for p in p.self_and_parents():
                d = self.vnodeOptionDict.get(p.v,{})
                # g.trace(p.h,d)
                for key in d.keys():
                    ivar = self.munge(key)
                    if not ivar in seen:
                        seen.append(ivar)
                        val = d.get(key)
                        self.setOption(key,val,p.h)

            # self.dumpSettings()
            if self.rst3_all:
                self.setOption("generate_rst", True, "rst3_all")
                self.setOption("generate_rst_header_comment",True, "rst3_all")
                self.setOption("http_server_support", True, "rst3_all")
                self.setOption("write_intermediate_file", True, "rst3_all")
        #@+node:ekr.20100811091636.5945: *6* initOptionsFromSettings
        def initOptionsFromSettings (self):

            c = self.c ; d = self.defaultOptionsDict
            keys = sorted(d)

            for key in keys:
                for getter,kind in (
                    (c.config.getBool,'@bool'),
                    (c.config.getString,'@string'),
                    (d.get,'default'),
                ):
                    val = getter(key)
                    if kind == 'default' or val is not None:
                        self.setOption(key,val,'initOptionsFromSettings')
                        break
            # Special case.
            if self.getOption('http_server_support') and not mod_http:
                g.es('No http_server_support: can not import mod_http plugin',color='red')
                self.setOption('http_server_support',False)
        #@+node:ekr.20100811091636.5946: *6* handleSingleNodeOptions
        def handleSingleNodeOptions (self,p):

            '''Init the settings of single-node options from the tnodeOptionsDict.

            All such options default to False.'''

            d = self.vnodeOptionDict.get(p.v, {} )

            for ivar in self.singleNodeOptions:
                val = d.get(ivar,False)
                #g.trace('%24s %8s %s' % (ivar,val,p.h))
                self.setOption(ivar,val,p.h)

        #@+node:ekr.20100811091636.5947: *5* setOption
        def setOption (self,name,val,tag):

            # if name == 'rst3_underline_characters':
                # g.trace(name,val,g.callers(4))

            ivar = self.munge(name)

            # bwm = False
            # if bwm:
                # if ivar not in self.optionsDict:
                    # g.trace('init %24s %20s %s %s' % (ivar, val, tag, self))
                # elif self.optionsDict.get(ivar) != val:
                    # g.trace('set  %24s %20s %s %s' % (ivar, val, tag, self))

            self.optionsDict [ivar] = val
        #@+node:ekr.20100811091636.5960: *4* write methods (leoRst)
        #@+node:ekr.20100811091636.5961: *5* getDocPart
        def getDocPart (self,lines,n):

            # g.trace('n',n,repr(''.join(lines)))

            result = []
            #@+<< Append whatever follows @doc or @space to result >>
            #@+node:ekr.20100811091636.5962: *6* << Append whatever follows @doc or @space to result >>
            if n > 0:
                line = lines[n-1]
                if line.startswith('@doc'):
                    s = line[4:].lstrip()
                elif line.startswith('@'):
                    s = line[1:].lstrip()
                else:
                    s = ''

                # New in Leo 4.4.4: remove these special tags.
                for tag in ('@rst-options','@rst-option','@rst-markup'):
                    if g.match_word(s,0,tag):
                        s = s[len(tag):].strip()

                if s.strip():
                    result.append(s)
            #@-<< Append whatever follows @doc or @space to result >>
            while n < len(lines):
                s = lines [n] ; n += 1
                if g.match_word(s,0,'@code') or g.match_word(s,0,'@c'):
                    break
                result.append(s)
            return n, result
        #@+node:ekr.20100811091636.5963: *5* handleCodeMode & helper
        def handleCodeMode (self,lines):

            '''Handle the preprocessed body text in code mode as follows:

            - Blank lines are copied after being cleaned.
            - @ @rst-markup lines get copied as is.
            - Everything else gets put into a code-block directive.'''

            result = [] ; n = 0 ; code = []
            while n < len(lines):
                s = lines [n] ; n += 1
                if (
                    self.isSpecialDocPart(s,'@rst-markup') or (
                        self.getOption('show_doc_parts_as_paragraphs') and
                        self.isSpecialDocPart(s,None)
                    )
                ):
                    if code:
                        self.finishCodePart(result,code)
                        code = []
                    result.append('')
                    n, lines2 = self.getDocPart(lines,n)
                    # A fix, perhaps dubious, to a bug discussed at
                    # http://groups.google.com/group/leo-editor/browse_thread/thread/c212814815c92aac
                    # lines2 = [z.lstrip() for z in lines2]
                    # g.trace('lines2',lines2)
                    result.extend(lines2)
                elif not s.strip() and not code:
                    pass # Ignore blank lines before the first code block.
                elif not code: # Start the code block.
                    result.append('')
                    result.append(self.code_block_string)
                    code.append(s)
                else: # Continue the code block.
                    code.append(s)

            if code:
                self.finishCodePart(result,code)
                code = []

            # Munge the result so as to keep docutils happy.
            # Don't use self.rstripList: it's not the same.
            # g.trace(result)
            result2 = []
            for z in result:
                if z == '': result2.append('\n\n')
                elif not z.rstrip(): pass
                elif z.endswith('\n\n'): result2.append(z) # Leave alone.
                else: result2.append('%s\n' % z.rstrip())

            return result2
        #@+node:ekr.20100811091636.5964: *6* formatCodeModeLine
        def formatCodeModeLine (self,s,n,numberOption):

            if not s.strip(): s = ''

            if numberOption:
                return '\t%d: %s' % (n,s)
            else:
                return '\t%s' % s
        #@+node:ekr.20100811091636.5965: *6* rstripList
        def rstripList (self,theList):

            '''Removed trailing blank lines from theList.'''

            s = '\n'.join(theList).rstrip()
            return s.split('\n')
        #@+node:ekr.20100811091636.5966: *6* finishCodePart
        def finishCodePart (self,result,code):

            numberOption = self.getOption('number_code_lines')
            code = self.rstripList(code)
            i = 0
            for line in code:
                i += 1
                result.append(self.formatCodeModeLine(line,i,numberOption))
        #@+node:ekr.20100811091636.5967: *5* handleDocOnlyMode
        def handleDocOnlyMode (self,p,lines):

            '''Handle the preprocessed body text in doc_only mode as follows:

            - Blank lines are copied after being cleaned.
            - @ @rst-markup lines get copied as is.
            - All doc parts get copied.
            - All code parts are ignored.'''

            ignore              = self.getOption('ignore_this_headline')
            showHeadlines       = self.getOption('show_headlines')
            showThisHeadline    = self.getOption('show_this_headline')
            showOrganizers      = self.getOption('show_organizer_nodes')

            result = [] ; n = 0
            while n < len(lines):
                s = lines [n] ; n += 1
                if self.isSpecialDocPart(s,'@rst-options'):
                    n, lines2 = self.getDocPart(lines,n) # ignore.
                elif self.isAnyDocPart(s):
                    # Handle any other doc part, including @rst-markup.
                    n, lines2 = self.getDocPart(lines,n)
                    if lines2: result.extend(lines2)
            if not result: result = []
            if showHeadlines:
                if result or showThisHeadline or showOrganizers or p == self.topNode:
                    # g.trace(len(result),p.h)
                    self.writeHeadlineHelper(p)
            return result
        #@+node:ekr.20100811091636.5968: *5* handleSpecialDocParts
        def handleSpecialDocParts (self,lines,kind,retainContents,asClass=None):

            # g.trace(kind,g.listToString(lines))

            result = [] ; n = 0
            while n < len(lines):
                s = lines [n] ; n += 1
                if s.strip().endswith('::'):
                    n, lit = self.skip_literal_block(lines,n-1)
                    result.extend(lit)
                elif self.isSpecialDocPart(s,kind):
                    n, lines2 = self.getDocPart(lines,n)
                    if retainContents:
                        result.extend([''])
                        if asClass:
                            result.extend(['.. container:: '+asClass, ''])
                            if 'literal' in asClass.split():
                                result.extend(['  ::', ''])
                            for l2 in lines2: result.append('    '+l2)
                        else:
                            result.extend(lines2)
                        result.extend([''])
                else:
                    result.append(s)

            return result
        #@+node:ekr.20100811091636.5969: *5* isAnyDocPart
        def isAnyDocPart (self,s):

            if s.startswith('@doc'):
                return True
            elif not s.startswith('@'):
                return False
            else:
                return len(s) == 1 or s[1].isspace()
        #@+node:ekr.20100811091636.5970: *5* isAnySpecialDocPart
        def isAnySpecialDocPart (self,s):

            for kind in (
                '@rst-markup',
                '@rst-option',
                '@rst-options',
            ):
                if self.isSpecialDocPart(s,kind):
                    return True

            return False
        #@+node:ekr.20100811091636.5971: *5* isSpecialDocPart
        def isSpecialDocPart (self,s,kind):

            '''Return True if s is a special doc part of the indicated kind.

            If kind is None, return True if s is any doc part.'''

            if s.startswith('@') and len(s) > 1 and s[1].isspace():
                if kind:
                    i = g.skip_ws(s,1)
                    result = g.match_word(s,i,kind)
                else:
                    result = True
            elif not kind:
                result = g.match_word(s,0,'@doc') or g.match_word(s,0,'@')
            else:
                result = False

            # g.trace('kind %s, result %s, s %s' % (
                # repr(kind),result,repr(s)))

            return result
        #@+node:ekr.20100811091636.5972: *5* removeLeoDirectives
        def removeLeoDirectives (self,lines):

            '''Remove all Leo directives, except within literal blocks.'''

            n = 0 ; result = []
            while n < len(lines):
                s = lines [n] ; n += 1
                if s.strip().endswith('::'):
                    n, lit = self.skip_literal_block(lines,n-1)
                    result.extend(lit)
                elif s.startswith('@') and not self.isAnySpecialDocPart(s):
                    for key in self.leoDirectivesList:
                        if g.match_word(s,0,key):
                            # g.trace('removing %s' % s)
                            break
                    else:
                        result.append(s)
                else:
                    result.append(s)

            return result
        #@+node:ekr.20100811091636.5973: *5* replaceCodeBlockDirectives
        def replaceCodeBlockDirectives (self,lines):

            '''Replace code-block directive, but not in literal blocks.'''

            n = 0 ; result = []
            while n < len(lines):
                s = lines [n] ; n += 1
                if s.strip().endswith('::'):
                    n, lit = self.skip_literal_block(lines,n-1)
                    result.extend(lit)
                else:
                    i = g.skip_ws(s,0)
                    if g.match(s,i,'..'):
                        i = g.skip_ws(s,i+2)
                        if g.match_word(s,i,'code-block'):
                            if 1: # Create a literal block to hold the code.
                                result.append('::\n')
                            else: # This 'annotated' literal block is confusing.
                                result.append('%s code::\n' % s[i+len('code-block'):])
                        else:
                            result.append(s)
                    else:
                        result.append(s)

            return result
        #@+node:ekr.20100811091636.5974: *5* skip_literal_block
        def skip_literal_block (self,lines,n):

            s = lines[n] ; result = [s] ; n += 1
            indent = g.skip_ws(s,0)

            # Skip lines until a non-blank line is found with same or less indent.
            while n < len(lines):
                s = lines[n]
                indent2 = g.skip_ws(s,0)
                if s and not s.isspace() and indent2 <= indent:
                    break # We will rescan lines [n]
                n += 1
                result.append(s)

            # g.printList(result,tag='literal block')
            return n, result
        #@+node:ekr.20100811091636.5975: *5* write (leoRst)
        def write (self,s,theFile=None):

            if theFile is None:
                theFile = self.outputFile

            if g.isPython3:
                if g.is_binary_file(theFile):
                    s = self.encode(s)
            else:
                s = self.encode(s)

            theFile.write(s)
        #@+node:ekr.20100811091636.5976: *5* writeBody
        def writeBody (self,p):

            # g.trace(p.h,p.b)

            # remove trailing cruft and split into lines.
            lines = g.splitLines(p.b)

            if self.getOption('code_mode'):
                if not self.getOption('show_options_doc_parts'):
                    lines = self.handleSpecialDocParts(lines,'@rst-options',
                        retainContents=False)
                if not self.getOption('show_markup_doc_parts'):
                    lines = self.handleSpecialDocParts(lines,'@rst-markup',
                        retainContents=False)
                if not self.getOption('show_leo_directives'):
                    lines = self.removeLeoDirectives(lines)
                lines = self.handleCodeMode(lines)
            elif self.getOption('doc_only_mode'):
                # New in version 1.15
                lines = self.handleDocOnlyMode(p,lines)
            else:
                lines = self.handleSpecialDocParts(lines,'@rst-options',
                    retainContents=False)
                lines = self.handleSpecialDocParts(lines,'@rst-markup',
                    retainContents=self.getOption('generate_rst'))
                if self.getOption('show_doc_parts_in_rst_mode') is True:
                    pass  # original behaviour, treat as plain text
                elif self.getOption('show_doc_parts_in_rst_mode'):
                    # use value as class for content
                    lines = self.handleSpecialDocParts(lines,None,
                        retainContents=True, asClass=self.getOption('show_doc_parts_in_rst_mode'))
                else:  # option evaluates to false, cut them out
                    lines = self.handleSpecialDocParts(lines,None,
                        retainContents=False)
                lines = self.removeLeoDirectives(lines)
                if self.getOption('generate_rst') and self.getOption('use_alternate_code_block'):
                    lines = self.replaceCodeBlockDirectives(lines)

            # Write the lines.
            s = ''.join(lines)

            # We no longer add newlines to the start of nodes because
            # we write a blank line after all sections.
            # s = g.ensureLeadingNewlines(s,1)
            s = g.ensureTrailingNewlines(s,2)
            self.write(s)
        #@+node:ekr.20100811091636.5977: *5* writeHeadline & helper
        def writeHeadline (self,p):

            '''Generate an rST section if options permit it.
            Remove headline commands from the headline first,
            and never generate an rST section for @rst-option and @rst-options.'''

            docOnly             =  self.getOption('doc_only_mode')
            ignore              = self.getOption('ignore_this_headline')
            showHeadlines       = self.getOption('show_headlines')
            showThisHeadline    = self.getOption('show_this_headline')
            showOrganizers      = self.getOption('show_organizer_nodes')

            if (
                p == self.topNode or
                ignore or
                docOnly or # handleDocOnlyMode handles this.
                not showHeadlines and not showThisHeadline or
                # docOnly and not showOrganizers and not thisHeadline or
                not p.h.strip() and not showOrganizers or
                not p.b.strip() and not showOrganizers
            ):
                return

            self.writeHeadlineHelper(p)
        #@+node:ekr.20100811091636.5978: *6* writeHeadlineHelper
        def writeHeadlineHelper (self,p):

            h = p.h
            if not self.atAutoWrite:
                h = h.strip()

            # Remove any headline command before writing the headline.
            i = g.skip_ws(h,0)
            i = g.skip_id(h,0,chars='@-')
            word = h [:i].strip()
            if word:
                # Never generate a section for @rst-option or @rst-options or @rst-no-head.
                if word in (
                    self.getOption('option_prefix'),
                    self.getOption('options_prefix'),
                    self.getOption('ignore_headline_prefix'), # Bug fix: 2009-5-13
                    self.getOption('ignore_headlines_prefix'),  # Bug fix: 2009-5-13
                ):
                    return
                # Remove all other headline commands from the headline.
                for prefix in self.headlineCommands:
                    if word == prefix:
                        h = h [len(word):].strip()
                        break

                # New in Leo 4.4.4.
                if word.startswith('@'):
                    if self.getOption('strip_at_file_prefixes'):
                        for s in ('@auto','@file','@nosent','@thin',):
                            if g.match_word(word,0,s):
                                h = h [len(s):].strip()

            if not h.strip(): return

            if self.getOption('show_sections'):
                if self.getOption('generate_rst'):
                    self.write(self.underline(h,p)) # Used by @auto-rst.
                else:
                    self.write('\n%s\n\n' % h)
            else:
                self.write('\n**%s**\n\n' % h.replace('*',''))
        #@+node:ekr.20100811091636.5979: *5* writeNode (rst)
        def writeNode (self,p):

            '''Format a node according to the options presently in effect.'''

            self.initCodeBlockString(p)
            self.scanAllOptions(p)

            if 0:
                g.trace('%24s code_mode %s' % (p.h,self.getOption('code_mode')))

            h = p.h.strip()

            if self.getOption('preformat_this_node'):
                self.http_addNodeMarker(p)
                self.writePreformat(p)
                p.moveToThreadNext()
            elif self.getOption('ignore_this_tree'):
                p.moveToNodeAfterTree()
            elif self.getOption('ignore_this_node'):
                p.moveToThreadNext()
            elif g.match_word(h,0,'@rst-options') and not self.getOption('show_options_nodes'):
                p.moveToThreadNext()
            else:
                self.http_addNodeMarker(p)
                self.writeHeadline(p)
                self.writeBody(p)
                p.moveToThreadNext()
        #@+node:ekr.20100811091636.5980: *5* writePreformat
        def writePreformat (self,p):

            '''Write p's body text lines as if preformatted.

             ::

                line 1
                line 2 etc.
            '''

            # g.trace(p.h,g.callers())

            lines = p.b.split('\n')
            lines = [' '*4 + z for z in lines]
            lines.insert(0,'::\n')

            s = '\n'.join(lines)
            if s.strip():
                self.write('%s\n\n' % s)
        #@+node:ekr.20100811091636.5981: *5* writeTree
        def writeTree(self,p):

            '''Write p's tree to self.outputFile.'''

            self.scanAllOptions(p)

            # g.trace(self.getOption('generate_rst_header_comment'))

            if self.getOption('generate_rst'):
                if self.getOption('generate_rst_header_comment'):
                    self.write(self.rstComment(
                        'rst3: filename: %s\n\n' % self.outputFileName))

            # We can't use an iterator because we may skip parts of the tree.
            p = p.copy() # Only one copy is needed for traversal.
            self.topNode = p.copy() # Indicate the top of this tree.
            after = p.nodeAfterTree()
            while p and p != after:
                self.writeNode(p) # Side effect: advances p.
        #@+node:ekr.20100811091636.5982: *4* Utils
        #@+node:ekr.20100811091636.5984: *5* encode
        def encode (self,s):

            # g.trace(self.encoding)

            return g.toEncodedString(s,encoding=self.encoding,reportErrors=True)
        #@+node:ekr.20100811091636.5985: *5* report
        def report (self,name):

            if self.getOption('verbose'):

                name = g.os_path_finalize(name)

                g.es_print('wrote: %s' % (name),color="blue")
        #@+node:ekr.20100811091636.5986: *5* rstComment
        def rstComment (self,s):

            return '.. %s' % s
        #@+node:ekr.20100811091636.5987: *5* underline (leoRst)
        def underline (self,s,p):

            '''Return the underlining string to be used at the given level for string s.
            This includes the headline, and possibly a leading overlining line.
            '''

            trace = False and not g.unitTesting

            if self.atAutoWrite:
                # We *might* generate overlines for top-level sections.
                u = self.atAutoWriteUnderlines
                level = p.level()-self.topLevel

                if trace: g.trace('level: %s under2: %s under1: %s %s' % (
                    level,repr(self.underlines2),repr(self.underlines1),p.h))

                # This is tricky. The index n depends on several factors.
                if self.underlines2:
                    level -= 1 # There *is* a double-underlined section.
                    n = level
                else:
                    n = level-1

                if 0 <= n < len(u):
                    ch = u[n]
                elif u:
                    ch = u[-1]
                else:
                    g.trace('can not happen: no u')
                    ch = '#'

                # 2010/01/10: write longer underlines for non-ascii characters.
                n = max(4,len(g.toEncodedString(s,encoding=self.encoding,reportErrors=False)))
                if trace: g.trace(self.topLevel,p.level(),level,repr(ch),p.h)
                if level == 0 and self.underlines2:
                    return '%s\n%s\n%s\n\n' % (ch*n,p.h,ch*n)
                else:
                    return '%s\n%s\n\n' % (p.h,ch*n)
            else:
                # The user is responsible for top-level overlining.
                u = self.getOption('underline_characters') #  '''#=+*^~"'`-:><_'''
                level = max(0,p.level()-self.topLevel)
                level = min(level+1,len(u)-1) # Reserve the first character for explicit titles.
                ch = u [level]
                if trace: g.trace(self.topLevel,p.level(),level,repr(ch),p.h)
                n = max(4,len(g.toEncodedString(s,encoding=self.encoding,reportErrors=False)))
                return '%s\n%s\n\n' % (p.h.strip(),ch*n)
        #@-others
    #@-others

formatController(c,defaultOptionsDict).run()
#@-others
#@-leo
