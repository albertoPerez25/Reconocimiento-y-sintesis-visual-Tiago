// generated from rosidl_generator_cpp/resource/idl__traits.hpp.em
// with input from play_motion2_msgs:srv/AddMotion.idl
// generated code does not contain a copyright notice

#ifndef PLAY_MOTION2_MSGS__SRV__DETAIL__ADD_MOTION__TRAITS_HPP_
#define PLAY_MOTION2_MSGS__SRV__DETAIL__ADD_MOTION__TRAITS_HPP_

#include <stdint.h>

#include <sstream>
#include <string>
#include <type_traits>

#include "play_motion2_msgs/srv/detail/add_motion__struct.hpp"
#include "rosidl_runtime_cpp/traits.hpp"

// Include directives for member types
// Member 'motion'
#include "play_motion2_msgs/msg/detail/motion__traits.hpp"

namespace play_motion2_msgs
{

namespace srv
{

inline void to_flow_style_yaml(
  const AddMotion_Request & msg,
  std::ostream & out)
{
  out << "{";
  // member: motion
  {
    out << "motion: ";
    to_flow_style_yaml(msg.motion, out);
    out << ", ";
  }

  // member: overwrite
  {
    out << "overwrite: ";
    rosidl_generator_traits::value_to_yaml(msg.overwrite, out);
  }
  out << "}";
}  // NOLINT(readability/fn_size)

inline void to_block_style_yaml(
  const AddMotion_Request & msg,
  std::ostream & out, size_t indentation = 0)
{
  // member: motion
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "motion:\n";
    to_block_style_yaml(msg.motion, out, indentation + 2);
  }

  // member: overwrite
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "overwrite: ";
    rosidl_generator_traits::value_to_yaml(msg.overwrite, out);
    out << "\n";
  }
}  // NOLINT(readability/fn_size)

inline std::string to_yaml(const AddMotion_Request & msg, bool use_flow_style = false)
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

}  // namespace play_motion2_msgs

namespace rosidl_generator_traits
{

[[deprecated("use play_motion2_msgs::srv::to_block_style_yaml() instead")]]
inline void to_yaml(
  const play_motion2_msgs::srv::AddMotion_Request & msg,
  std::ostream & out, size_t indentation = 0)
{
  play_motion2_msgs::srv::to_block_style_yaml(msg, out, indentation);
}

[[deprecated("use play_motion2_msgs::srv::to_yaml() instead")]]
inline std::string to_yaml(const play_motion2_msgs::srv::AddMotion_Request & msg)
{
  return play_motion2_msgs::srv::to_yaml(msg);
}

template<>
inline const char * data_type<play_motion2_msgs::srv::AddMotion_Request>()
{
  return "play_motion2_msgs::srv::AddMotion_Request";
}

template<>
inline const char * name<play_motion2_msgs::srv::AddMotion_Request>()
{
  return "play_motion2_msgs/srv/AddMotion_Request";
}

template<>
struct has_fixed_size<play_motion2_msgs::srv::AddMotion_Request>
  : std::integral_constant<bool, has_fixed_size<play_motion2_msgs::msg::Motion>::value> {};

template<>
struct has_bounded_size<play_motion2_msgs::srv::AddMotion_Request>
  : std::integral_constant<bool, has_bounded_size<play_motion2_msgs::msg::Motion>::value> {};

template<>
struct is_message<play_motion2_msgs::srv::AddMotion_Request>
  : std::true_type {};

}  // namespace rosidl_generator_traits

namespace play_motion2_msgs
{

namespace srv
{

inline void to_flow_style_yaml(
  const AddMotion_Response & msg,
  std::ostream & out)
{
  out << "{";
  // member: success
  {
    out << "success: ";
    rosidl_generator_traits::value_to_yaml(msg.success, out);
  }
  out << "}";
}  // NOLINT(readability/fn_size)

inline void to_block_style_yaml(
  const AddMotion_Response & msg,
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
}  // NOLINT(readability/fn_size)

inline std::string to_yaml(const AddMotion_Response & msg, bool use_flow_style = false)
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

}  // namespace play_motion2_msgs

namespace rosidl_generator_traits
{

[[deprecated("use play_motion2_msgs::srv::to_block_style_yaml() instead")]]
inline void to_yaml(
  const play_motion2_msgs::srv::AddMotion_Response & msg,
  std::ostream & out, size_t indentation = 0)
{
  play_motion2_msgs::srv::to_block_style_yaml(msg, out, indentation);
}

[[deprecated("use play_motion2_msgs::srv::to_yaml() instead")]]
inline std::string to_yaml(const play_motion2_msgs::srv::AddMotion_Response & msg)
{
  return play_motion2_msgs::srv::to_yaml(msg);
}

template<>
inline const char * data_type<play_motion2_msgs::srv::AddMotion_Response>()
{
  return "play_motion2_msgs::srv::AddMotion_Response";
}

template<>
inline const char * name<play_motion2_msgs::srv::AddMotion_Response>()
{
  return "play_motion2_msgs/srv/AddMotion_Response";
}

template<>
struct has_fixed_size<play_motion2_msgs::srv::AddMotion_Response>
  : std::integral_constant<bool, true> {};

template<>
struct has_bounded_size<play_motion2_msgs::srv::AddMotion_Response>
  : std::integral_constant<bool, true> {};

template<>
struct is_message<play_motion2_msgs::srv::AddMotion_Response>
  : std::true_type {};

}  // namespace rosidl_generator_traits

namespace rosidl_generator_traits
{

template<>
inline const char * data_type<play_motion2_msgs::srv::AddMotion>()
{
  return "play_motion2_msgs::srv::AddMotion";
}

template<>
inline const char * name<play_motion2_msgs::srv::AddMotion>()
{
  return "play_motion2_msgs/srv/AddMotion";
}

template<>
struct has_fixed_size<play_motion2_msgs::srv::AddMotion>
  : std::integral_constant<
    bool,
    has_fixed_size<play_motion2_msgs::srv::AddMotion_Request>::value &&
    has_fixed_size<play_motion2_msgs::srv::AddMotion_Response>::value
  >
{
};

template<>
struct has_bounded_size<play_motion2_msgs::srv::AddMotion>
  : std::integral_constant<
    bool,
    has_bounded_size<play_motion2_msgs::srv::AddMotion_Request>::value &&
    has_bounded_size<play_motion2_msgs::srv::AddMotion_Response>::value
  >
{
};

template<>
struct is_service<play_motion2_msgs::srv::AddMotion>
  : std::true_type
{
};

template<>
struct is_service_request<play_motion2_msgs::srv::AddMotion_Request>
  : std::true_type
{
};

template<>
struct is_service_response<play_motion2_msgs::srv::AddMotion_Response>
  : std::true_type
{
};

}  // namespace rosidl_generator_traits

#endif  // PLAY_MOTION2_MSGS__SRV__DETAIL__ADD_MOTION__TRAITS_HPP_
