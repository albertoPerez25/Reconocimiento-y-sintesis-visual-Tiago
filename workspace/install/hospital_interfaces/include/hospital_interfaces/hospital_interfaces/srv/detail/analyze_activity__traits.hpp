// generated from rosidl_generator_cpp/resource/idl__traits.hpp.em
// with input from hospital_interfaces:srv/AnalyzeActivity.idl
// generated code does not contain a copyright notice

#ifndef HOSPITAL_INTERFACES__SRV__DETAIL__ANALYZE_ACTIVITY__TRAITS_HPP_
#define HOSPITAL_INTERFACES__SRV__DETAIL__ANALYZE_ACTIVITY__TRAITS_HPP_

#include <stdint.h>

#include <sstream>
#include <string>
#include <type_traits>

#include "hospital_interfaces/srv/detail/analyze_activity__struct.hpp"
#include "rosidl_runtime_cpp/traits.hpp"

namespace hospital_interfaces
{

namespace srv
{

inline void to_flow_style_yaml(
  const AnalyzeActivity_Request & msg,
  std::ostream & out)
{
  out << "{";
  // member: image_path
  {
    out << "image_path: ";
    rosidl_generator_traits::value_to_yaml(msg.image_path, out);
    out << ", ";
  }

  // member: zone_name
  {
    out << "zone_name: ";
    rosidl_generator_traits::value_to_yaml(msg.zone_name, out);
    out << ", ";
  }

  // member: time
  {
    out << "time: ";
    rosidl_generator_traits::value_to_yaml(msg.time, out);
    out << ", ";
  }

  // member: expected_activities
  {
    out << "expected_activities: ";
    rosidl_generator_traits::value_to_yaml(msg.expected_activities, out);
    out << ", ";
  }

  // member: zone_type
  {
    out << "zone_type: ";
    rosidl_generator_traits::value_to_yaml(msg.zone_type, out);
  }
  out << "}";
}  // NOLINT(readability/fn_size)

inline void to_block_style_yaml(
  const AnalyzeActivity_Request & msg,
  std::ostream & out, size_t indentation = 0)
{
  // member: image_path
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "image_path: ";
    rosidl_generator_traits::value_to_yaml(msg.image_path, out);
    out << "\n";
  }

  // member: zone_name
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "zone_name: ";
    rosidl_generator_traits::value_to_yaml(msg.zone_name, out);
    out << "\n";
  }

  // member: time
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "time: ";
    rosidl_generator_traits::value_to_yaml(msg.time, out);
    out << "\n";
  }

  // member: expected_activities
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "expected_activities: ";
    rosidl_generator_traits::value_to_yaml(msg.expected_activities, out);
    out << "\n";
  }

  // member: zone_type
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "zone_type: ";
    rosidl_generator_traits::value_to_yaml(msg.zone_type, out);
    out << "\n";
  }
}  // NOLINT(readability/fn_size)

inline std::string to_yaml(const AnalyzeActivity_Request & msg, bool use_flow_style = false)
{
  std::ostringstream out;
  if (use_flow_style) {
    to_flow_style_yaml(msg, out);
  } else {
    to_block_style_yaml(msg, out);
  }
  return out.str();
}

}  // namespace srv

}  // namespace hospital_interfaces

namespace rosidl_generator_traits
{

[[deprecated("use hospital_interfaces::srv::to_block_style_yaml() instead")]]
inline void to_yaml(
  const hospital_interfaces::srv::AnalyzeActivity_Request & msg,
  std::ostream & out, size_t indentation = 0)
{
  hospital_interfaces::srv::to_block_style_yaml(msg, out, indentation);
}

[[deprecated("use hospital_interfaces::srv::to_yaml() instead")]]
inline std::string to_yaml(const hospital_interfaces::srv::AnalyzeActivity_Request & msg)
{
  return hospital_interfaces::srv::to_yaml(msg);
}

template<>
inline const char * data_type<hospital_interfaces::srv::AnalyzeActivity_Request>()
{
  return "hospital_interfaces::srv::AnalyzeActivity_Request";
}

template<>
inline const char * name<hospital_interfaces::srv::AnalyzeActivity_Request>()
{
  return "hospital_interfaces/srv/AnalyzeActivity_Request";
}

template<>
struct has_fixed_size<hospital_interfaces::srv::AnalyzeActivity_Request>
  : std::integral_constant<bool, false> {};

template<>
struct has_bounded_size<hospital_interfaces::srv::AnalyzeActivity_Request>
  : std::integral_constant<bool, false> {};

template<>
struct is_message<hospital_interfaces::srv::AnalyzeActivity_Request>
  : std::true_type {};

}  // namespace rosidl_generator_traits

namespace hospital_interfaces
{

namespace srv
{

inline void to_flow_style_yaml(
  const AnalyzeActivity_Response & msg,
  std::ostream & out)
{
  out << "{";
  // member: report
  {
    out << "report: ";
    rosidl_generator_traits::value_to_yaml(msg.report, out);
  }
  out << "}";
}  // NOLINT(readability/fn_size)

inline void to_block_style_yaml(
  const AnalyzeActivity_Response & msg,
  std::ostream & out, size_t indentation = 0)
{
  // member: report
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "report: ";
    rosidl_generator_traits::value_to_yaml(msg.report, out);
    out << "\n";
  }
}  // NOLINT(readability/fn_size)

inline std::string to_yaml(const AnalyzeActivity_Response & msg, bool use_flow_style = false)
{
  std::ostringstream out;
  if (use_flow_style) {
    to_flow_style_yaml(msg, out);
  } else {
    to_block_style_yaml(msg, out);
  }
  return out.str();
}

}  // namespace srv

}  // namespace hospital_interfaces

namespace rosidl_generator_traits
{

[[deprecated("use hospital_interfaces::srv::to_block_style_yaml() instead")]]
inline void to_yaml(
  const hospital_interfaces::srv::AnalyzeActivity_Response & msg,
  std::ostream & out, size_t indentation = 0)
{
  hospital_interfaces::srv::to_block_style_yaml(msg, out, indentation);
}

[[deprecated("use hospital_interfaces::srv::to_yaml() instead")]]
inline std::string to_yaml(const hospital_interfaces::srv::AnalyzeActivity_Response & msg)
{
  return hospital_interfaces::srv::to_yaml(msg);
}

template<>
inline const char * data_type<hospital_interfaces::srv::AnalyzeActivity_Response>()
{
  return "hospital_interfaces::srv::AnalyzeActivity_Response";
}

template<>
inline const char * name<hospital_interfaces::srv::AnalyzeActivity_Response>()
{
  return "hospital_interfaces/srv/AnalyzeActivity_Response";
}

template<>
struct has_fixed_size<hospital_interfaces::srv::AnalyzeActivity_Response>
  : std::integral_constant<bool, false> {};

template<>
struct has_bounded_size<hospital_interfaces::srv::AnalyzeActivity_Response>
  : std::integral_constant<bool, false> {};

template<>
struct is_message<hospital_interfaces::srv::AnalyzeActivity_Response>
  : std::true_type {};

}  // namespace rosidl_generator_traits

namespace rosidl_generator_traits
{

template<>
inline const char * data_type<hospital_interfaces::srv::AnalyzeActivity>()
{
  return "hospital_interfaces::srv::AnalyzeActivity";
}

template<>
inline const char * name<hospital_interfaces::srv::AnalyzeActivity>()
{
  return "hospital_interfaces/srv/AnalyzeActivity";
}

template<>
struct has_fixed_size<hospital_interfaces::srv::AnalyzeActivity>
  : std::integral_constant<
    bool,
    has_fixed_size<hospital_interfaces::srv::AnalyzeActivity_Request>::value &&
    has_fixed_size<hospital_interfaces::srv::AnalyzeActivity_Response>::value
  >
{
};

template<>
struct has_bounded_size<hospital_interfaces::srv::AnalyzeActivity>
  : std::integral_constant<
    bool,
    has_bounded_size<hospital_interfaces::srv::AnalyzeActivity_Request>::value &&
    has_bounded_size<hospital_interfaces::srv::AnalyzeActivity_Response>::value
  >
{
};

template<>
struct is_service<hospital_interfaces::srv::AnalyzeActivity>
  : std::true_type
{
};

template<>
struct is_service_request<hospital_interfaces::srv::AnalyzeActivity_Request>
  : std::true_type
{
};

template<>
struct is_service_response<hospital_interfaces::srv::AnalyzeActivity_Response>
  : std::true_type
{
};

}  // namespace rosidl_generator_traits

#endif  // HOSPITAL_INTERFACES__SRV__DETAIL__ANALYZE_ACTIVITY__TRAITS_HPP_
