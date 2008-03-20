"""
A converter for office docs.

Run this script without arguments to get help.

It needs an openoffice server running in background.

Lots of this code was taken from the official OOo documentation for
Python programmers.

  http://udk.openoffice.org/python/samples/ooextract.py

"""
import getopt, sys
from os import getcwd
from os.path import splitext

# The following wierd registratrion stuff must happen due to the fact,
# that Zope does not cope with the uno ``__import__`` replacement
# (which in fact is in a bad shape). There are different places in the
# Zope machinery, that require the original ``__import__`` function,
# because they make too much assumptions about modules, ImportErrors
# and the tracebacks they might produce. Therefore there are several
# places to blame for that mess.
#
# We disable the uno ``__import__`` function after importing uno and
# have to enable it at places, where uno-functionality is needed.
#
# Never import ``uno`` in your Zope code. If you do, use the register
# and unregister functions below immediately before and after using
# it.
#
# If you know of a decent implementation of ``__import__`` for the uno
# module, I would like to hear of it.
#
#                                                -- Uli
#
import __builtin__
_orig__import = __builtin__.__dict__['__import__']
import uno
_uno__import = uno.__dict__['_uno_import']


def register_uno_import():
    __builtin__.__dict__['__import__'] = _uno__import

def unregister_uno_import():
    __builtin__.__dict__['__import__'] = _orig__import

unregister_uno_import()

def convert_to_html(
    url="uno:socket,host=localhost,port=2002;urp;StarOffice.ComponentContext",
    filter_name="HTML (StarWriter)",
    extension="html",
    path=None):
    """Convert the document in ``path`` to HTML.

    Returns the HTML text. Any subobjects are placed as files in the
    document path.
    """
    return convert(url, filter_name, extension, paths=[path])

def convert_to_pdf(
    url="uno:socket,host=localhost,port=2002;urp;StarOffice.ComponentContext",
    filter_name="writer_pdf_Export",
    extension="pdf",
    path=None):
    """Convert the document in ``path`` to PDF.
    
    Returns the PDF document as string. Any subobjects are placed as
    files in the document path.
    """
    return convert(url, filter_name, extension, paths=[path])

def convert(
    url="uno:socket,host=localhost,port=2002;urp;StarOffice.ComponentContext",
    filter_name="Text (Encoded)",
    extension="txt",
    paths=[]):
    """Do the real conversion.
    """
    # This deferred imports and in-class definitions are due to the
    # Plone test runner, which seems to have problems with pyuno
    # loaded at testing time.
    register_uno_import()
    from unohelper import Base, systemPathToFileUrl, absolutize
    from com.sun.star.beans import PropertyValue
    from com.sun.star.uno import Exception as UnoException
    from com.sun.star.io import IOException, XOutputStream
    unregister_uno_import()

    class OutputStream(Base, XOutputStream):
        def __init__(self):
            self.closed = 0
        def closeOutput(self):
            self.closed = 1
        def writeBytes(self, seq):
            sys.stdout.write(seq.value)
        def flush(self):
            pass

    ret_val = 0
    doc = None
    stdout = False

    try:
        ctxLocal = uno.getComponentContext()
        smgrLocal = ctxLocal.ServiceManager

        resolver = smgrLocal.createInstanceWithContext(
                 "com.sun.star.bridge.UnoUrlResolver", ctxLocal)
        ctx = resolver.resolve(url)
        smgr = ctx.ServiceManager

        desktop = smgr.createInstanceWithContext(
            "com.sun.star.frame.Desktop", ctx)

        cwd = systemPathToFileUrl(getcwd())
        outProps = (
            PropertyValue("FilterName" , 0, filter_name , 0),
	    PropertyValue("Overwrite" , 0, True , 0),
            PropertyValue("OutputStream", 0, OutputStream(), 0)
	)
	    
        inProps = PropertyValue("Hidden" , 0 , True, 0),
        for path in paths:
            try:
                fileUrl = absolutize(cwd, systemPathToFileUrl(path))
                doc = desktop.loadComponentFromURL(
                    fileUrl , "_blank", 0, inProps)

                if not doc:
                    raise UnoException(
                        "Couldn't open stream for unknown reason", None)

		if not stdout:
                    (dest, ext) = splitext(path)
                    dest = dest + "." + extension
                    destUrl = absolutize(cwd, systemPathToFileUrl(dest))
                    doc.storeToURL(destUrl, outProps)
		else:
		    doc.storeToURL("private:stream",outProps)
            except IOException, e:
                print "Error during conversion: ", e.Message
                ret_val = 1
            except UnoException, e:
                print "UnoError during conversion: ", e.__class__, e.Message
                ret_val = 1
            if doc:
                doc.dispose()

    except UnoException, e:
        sys.stderr.write(
            "Error ("+repr(e.__class__)+") :" + e.Message + "\n")
        ret_val = 1
        
    return ret_val

def usage():
    sys.stderr.write(
        "usage: ooextract.py --help | --stdout\n"+
        "       [-c <connection-string> | --connection-string=<connection-string>\n"+
        "       [--html|--pdf]\n"+
        "       [--stdout]\n"+
        "       file1 file2 ...\n"+
        "\n" +
        "Extracts plain text from documents and prints it to a file (unless --stdout is specified).\n" +
        "Requires an OpenOffice.org instance to be running. The script and the\n"+
        "running OpenOffice.org instance must be able to access the file with\n"+
        "by the same system path. [ To have a listening OpenOffice.org instance, just run:\n"+
        "openoffice \"-accept=socket,host=localhost,port=2002;urp;\" \n"
        "\n"+
        "--stdout \n" +
        "         Redirect output to stdout. Avoids writing to a file directly\n" + 
        "-c <connection-string> | --connection-string=<connection-string>\n" +
        "        The connection-string part of a uno url to where the\n" +
        "        the script should connect to in order to do the conversion.\n" +
        "        The strings defaults to socket,host=localhost,port=2002\n"
        "--html \n"
        "        Instead of the text filter, the writer html filter is used\n"
        "--pdf \n"
        "        Instead of the text filter, the pdf filter is used\n"
        )
    

def main(argv=sys.argv):
    try:
        opts, args = getopt.getopt(sys.argv[1:], "hc:",
            ["help", "connection-string=" , "html", "pdf", "stdout" ])
        url = "uno:socket,host=localhost,port=2002;urp;StarOffice.ComponentContext"
        filter_name = "Text (Encoded)"
        extension  = "txt"
        for o, a in opts:
            if o in ("-h", "--help"):
                usage()
                sys.exit()
            if o in ("-c", "--connection-string"):
                url = "uno:" + a + ";urp;StarOffice.ComponentContext"
            if o == "--html":
                filter_name = "HTML (StarWriter)"
                extension  = "html"
            if o == "--pdf":
                filter_name = "writer_pdf_Export"
                extension  = "pdf"
	    if o == "--stdout":
	    	stdout = True
                
        if not len(args):
            usage()
            sys.exit()
            
        ret_val = convert(url, filter_name, extension, args)

    except getopt.GetoptError,e:
        sys.stderr.write(str(e) + "\n")
        usage()
        ret_val = 1
    sys.exit(ret_val)



if __name__ == '__main__':
    main(argv=sys.argv)
