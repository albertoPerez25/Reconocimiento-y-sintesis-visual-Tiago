// generated from rosidl_generator_cpp/resource/idl__traits.hpp.em
// with input from hospital_interfaces:srv/GetPatrolContext.idl
// generated code does not contain a copyright notice

#ifndef HOSPITAL_INTERFACES__SRV__DETAIL__GET_PATROL_CONTEXT__TRAITS_HPP_
#define HOSPITAL_INTERFACES__SRV__DETAIL__GET_PATROL_CONTEXT__TRAITS_HPP_

#include <stdint.h>

#include <sstream>
#include <string>
#include <type_traits>

#include "hospital_interfaces/srv/detail/get_patrol_context__struct.hpp"
#include "rosidl_runtime_cpp/traits.hpp"

namespace hospital_interfaces
{

namespace srv
{

inline void to_flow_style_yaml(
  const GetPatrolContext_Request & msg,
  std::ostream & out)
{
  (void)msg;
  out << "null";
}  // NOLINT(readability/fn_size)

inline void to_block_style_yaml(
  const GetPatrolContext_Request & msg,
  std::ostream & out, size_t indentation = 0)
{
  (void)msg;
  (void)indentation;
  out << "null\n";
}  // NOLINT(readability/fn_size)

inline std::string to_yaml(const GetPatrolContext_Request & msg, bool use_flow_style = false)
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
  const hospital_interfaces::srv::GetPatrolContext_Request & msg,
  std::ostream & out, size_t indentation = 0)
{
  hospital_interfaces::srv::to_block_style_yaml(msg, out, indentation);
}

[[deprecated("use hospital_interfaces::srv::to_yaml() instead")]]
inline std::string to_yaml(const hospital_interfaces::srv::GetPatrolContext_Request & msg)
{
  return hospital_interfaces::srv::to_yaml(msg);
}

template<>
inline const char * data_type<hospital_interfaces::srv::GetPatrolContext_Request>()
{
  return "hospital_interfaces::srv::GetPatrolContext_Request";
}

template<>
inline const char * name<hospital_interfaces::srv::GetPatrolContext_Request>()
{
  return "hospital_interfaces/srv/GetPatrolContext_Request";
}

template<>
struct has_fixed_size<hospital_interfaces::srv::GetPatrolContext_Request>
  : std::integral_constant<bool, true> {};

template<>
struct has_bounded_size<hospital_interfaces::srv::GetPatrolContext_Request>
  : std::integral_constant<bool, true> {};

template<>
struct is_message<hospital_interfaces::srv::GetPatrolContext_Request>
  : std::true_type {};

}  // namespace rosidl_generator_traits

namespace hospital_interfaces
{

namespace srv
{

inline void to_flow_style_yaml(
  const GetPatrolContext_Response & msg,
  std::ostream & out)
{
  out << "{";
  // member: success
  {
    out << "success: ";
    rosidl_generator_traits::value_to_yaml(msg.success, out);
    out << ", ";
  }

  // member: global_context
  {
    out << "global_context: ";
    rosidl_generator_traits::value_to_yaml(msg.global_context, out);
    out << ", ";
  }

  // member: final_summary
  {
    out << "final_summary: ";
    rosidl_generator_traits::value_to_yaml(msg.final_summary, out);
  }
  out << "}";
}  // NOLINT(readability/fn_size)

inline void to_block_style_yaml(
  const GetPatrolContext_Response & msg,
  std::ostream & out, size_t indentation = 0)
{
  // member: success
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "success: ";
    rosidl_generator_traits::value_to_yaml(msg.success, out);
    out << "\n";
  }

  // member: global_context
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "global_context: ";
    rosidl_generator_traits::value_to_yaml(msg.global_context, out);
    out << "\n";
  }

  // member: final_summary
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "final_summary: ";
    rosidl_generator_traits::value_to_yaml(msg.final_summary, out);
    out << "\n";
  }
}  // NOLINT(readability/fn_size)

inline std::string to_yaml(const GetPatrolContext_Response & msg, bool use_flow_style = false)
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
  const hospital_interfaces::srv::GetPatrolContext_Response & msg,
  std::ostream & out, size_t indentation = 0)
{
  hospital_interfaces::srv::to_block_style_yaml(msg, out, indentation);
}

[[deprecated("use hospital_interfaces::srv::to_yaml() instead")]]
inline std::string to_yaml(const hospital_interfaces::srv::GetPatrolContext_Response & msg)
{
  return hospital_interfaces::srv::to_yaml(msg);
}

template<>
inline const char * data_type<hospital_interfaces::srv::GetPatrolContext_Response>()
{
  return "hospital_interfaces::srv::GetPatrolContext_Response";
}

template<>
inline const char * name<hospital_interfaces::srv::GetPatrolContext_Response>()
{
  return "hospital_interfaces/srv/GetPatrolContext_Response";
}

template<>
struct has_fixed_size<hospital_interfaces::srv::GetPatrolContext_Response>
  : std::integral_constant<bool, false> {};

template<>
struct has_bounded_size<hospital_interfaces::srv::GetPatrolContext_Response>
  : std::integral_constant<bool, false> {};

template<>
struct is_message<hospital_interfaces::srv::GetPatrolContext_Response>
  : std::true_type {};

}  // namespace rosidl_generator_traits

namespace rosidl_generator_traits
{

template<>
inline const char * data_type<hospital_interfaces::srv::GetPatrolContext>()
{
  return "hospital_interfaces::srv::GetPatrolContext";
}

template<>
inline const char * name<hospital_interfaces::srv::GetPatrolContext>()
{
  return "hospital_interfaces/srv/GetPatrolContext";
}

template<>
struct has_fixed_size<hospital_interfaces::srv::GetPatrolContext>
  : std::integral_constant<
    bool,
    has_fixed_size<hospital_interfaces::srv::GetPatrolContext_Request>::value &&
    has_fixed_size<hospital_interfaces::srv::GetPatrolContext_Response>::value
  >
{
};

template<>
struct has_bounded_size<hospital_interfaces::srv::GetPatrolContext>
  : std::integral_constant<
    bool,
    has_bounded_size<hospital_interfaces::srv::GetPatrolContext_Request>::value &&
    has_bounded_size<hospital_interfaces::srv::GetPatrolContext_Response>::value
  >
{
};

template<>
struct is_service<hospital_interfaces::srv::GetPatrolContext>
  : std::true_type
{
};

template<>
struct is_service_request<hospital_interfaces::srv::GetPatrolContext_Request>
  : std::true_type
{
};

template<>
struct is_service_response<hospital_interfaces::srv::GetPatrolContext_Response>
  : std::true_type
{
};

}  // namespace rosidl_generator_traits

#endif  // HOSPITAL_INTERFACES__SRV__DETAIL__GET_PATROL_CONTEXT__TRAITS_HPP_
