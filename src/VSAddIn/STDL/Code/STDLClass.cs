using System.Collections.Generic;
using System.Text;
using EnvDTE;
using System.Diagnostics;

namespace STDL.Code
{
    public class STDLClass
    {
        private string _namespace;
        private string _className;
        private readonly IList<STDLFunction> _functions = new List<STDLFunction>();
        private readonly IDictionary<string, string> _requiredNamespaces = new Dictionary<string, string>();

        public STDLClass(FileCodeModel model)
        {
            CodeElements elements = model.CodeElements;
            foreach (CodeElement element in elements)
            {
                Walk(element);
            }

            foreach (STDLFunction functionCode in _functions)
            {
                foreach (KeyValuePair<string, string> pair in functionCode.RequiredNamespaces)
                {
                    if (!_requiredNamespaces.ContainsKey(pair.Key))
                        _requiredNamespaces.Add(pair.Key, pair.Value);
                }
            }
        }

        public override string ToString()
        {
            StringBuilder builder = new StringBuilder();
            builder.AppendLine("init:");
            builder.Append("\t");
            //editPt.Insert("language:" + clazz.Model.Language + Environment.NewLine);
            builder.AppendLine("language:CS2");
            builder.Append("\t");
            builder.AppendLine("classname:" + _className);
            builder.Append("\t");
            builder.AppendLine("namespace:" + _namespace);
            foreach (string @namespace in _requiredNamespaces.Keys)
            {
                builder.Append("\t");
                builder.AppendLine("language_imports:" + @namespace);
            }

            builder.AppendLine();
            foreach (STDLFunction function in _functions)
            {
                builder.Append(function.ToString());
            }
            return builder.ToString();
        }
        
        public string ClassName
        {
            get { return _className; }
        }

        private void Walk(CodeElement element)
        {
            switch(element.Kind)
            {
                case vsCMElement.vsCMElementImportStmt:
                    Trace.WriteLine("Uncaught: " + element.Kind);
                    break;
                case vsCMElement.vsCMElementNamespace:
                    _namespace = element.Name;
                    break;
                case vsCMElement.vsCMElementClass:
                    _className = element.Name;
                    break;
                case vsCMElement.vsCMElementFunction:
                    _functions.Add(new STDLFunction(element as CodeFunction));
                    break;
                case vsCMElement.vsCMElementProperty:
                    Trace.WriteLine("Uncaught: " + element.Kind + ":" + element.Name);
                    break;
                default:
                    Trace.WriteLine("Uncaught: " + element.Kind);
                    break;
            }
            foreach (CodeElement codeElement in element.Children)
            {
                Walk(codeElement);
            }
        }
    }
}