using System.Text;
using EnvDTE;

namespace STDL.Code
{
    public class STDLParameter
    {
        private readonly string _name;
        private readonly STDLType _type;

        public STDLParameter(CodeParameter parameter)
        {
            _name = parameter.FullName;
            _type = new STDLType(parameter.Type);
        }

        public string Name
        {
            get { return _name; }
        }

        public override string ToString()
        {
            StringBuilder builder = new StringBuilder();
            builder.Append("\t");
            builder.AppendLine("param <%" + _type + "%> " + _name + ":");

            builder.Append("\t\t");
            builder.AppendLine("valid 0:");
            
            builder.Append("\t\t\t");
            builder.AppendLine(_name + " == " + _type.DefaultValue());
            return builder.ToString();
        }

        public STDLType Type
        {
            get { return _type; }
        }
    }
}
