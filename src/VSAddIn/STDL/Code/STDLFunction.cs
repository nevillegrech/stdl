using System.Collections.Generic;
using System.Text;
using EnvDTE;

namespace STDL.Code
{
    public class STDLFunction
    {
        private readonly string _name;
        private readonly IList<STDLParameter> _parameters = new List<STDLParameter>();
        private readonly STDLType _returnType;
        private readonly IDictionary<string, string> _namespaces;

        public STDLFunction(CodeFunction function)
        {
            _name = function.Name;
            _returnType = new STDLType(function.Type);
            
            _namespaces = new Dictionary<string, string>();
            string @namespace;
            int namespaceEnd = _returnType.FullName().LastIndexOf('.');
            if(namespaceEnd >= 0)
            {
                @namespace = _returnType.FullName().Substring(0, namespaceEnd);
                _namespaces.Add(@namespace, "");
            }
            
            foreach (CodeParameter parameter in function.Parameters)
            {
                STDLParameter item = new STDLParameter(parameter);
                _parameters.Add(item);
                @namespace = item.Type.FullName().Substring(0, item.Type.FullName().LastIndexOf('.'));
                if (!_namespaces.ContainsKey(@namespace))
                    _namespaces.Add(@namespace, "");
            }
        }

        public override string ToString()
        {
            StringBuilder builder = new StringBuilder();
            builder.Append("test TestName method <%" + _name + "(");
            bool first = true;
            foreach (STDLParameter parameter in _parameters)
            {
                if (!first)
                    builder.Append(", ");
                builder.Append("%" + parameter.Name + "%");
                first = false;
            }

            builder.AppendLine(")%> returns <%" + _returnType + "%>:");
            foreach (STDLParameter parameter in _parameters)
            {
                builder.Append(parameter.ToString());
                
            }
            builder.AppendLine("\t\tout:");
            builder.AppendLine("\t\treturns == " + _returnType.DefaultValue());
            builder.AppendLine();

            builder.AppendLine();
            return builder.ToString();
        }

        public IDictionary<string, string> RequiredNamespaces
        {
            get { return _namespaces; }
        }
    }
}