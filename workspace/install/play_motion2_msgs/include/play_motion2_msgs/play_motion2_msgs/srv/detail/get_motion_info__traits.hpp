// generated from rosidl_generator_cpp/resource/idl__traits.hpp.em
// with input from play_motion2_msgs:srv/GetMotionInfo.idl
// generated code does not contain a copyright notice

#ifndef PLAY_MOTION2_MSGS__SRV__DETAIL__GET_MOTION_INFO__TRAITS_HPP_
#define PLAY_MOTION2_MSGS__SRV__DETAIL__GET_MOTION_INFO__TRAITS_HPP_

#include <stdint.h>

#include <sstream>
#include <string>
#include <type_traits>

#include "play_motion2_msgs/srv/detail/get_motion_info__struct.hpp"
#include "rosidl_runtime_cpp/traits.hpp"

namespace play_motion2_msgs
{

namespace srv
{

inline void to_flow_style_yaml(
  const GetMotionInfo_Request & msg,
  std::ostream & out)
{
  out << "{";
  // member: motion_key
  {
    out << "motion_key: ";
    rosidl_generator_traits::value_to_yaml(msg.motion_key, out);
  }
  out << "}";
}  // NOLINT(readability/fn_size)

inline void to_block_style_yaml(
  const GetMotionInfo_Request & msg,
  std::ostream & out, size_t indentation = 0)
{
  // member: motion_key
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "motion_key: ";
    rosidl_generator_traits::value_to_yaml(msg.motion_key, out);
    out << "\n";
  }
}  // NOLINT(readability/fn_size)

inline std::string to_yaml(const GetMotionInfo_Request & msg, bool use_flow_style = false)
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
  const play_motion2_msgs::srv::GetMotionInfo_Request & msg,
  std::ostream & out, size_t indentation = 0)
{
  play_motion2_msgs::srv::to_block_style_yaml(msg, out, indentation);
}

[[deprecated("use play_motion2_msgs::srv::to_yaml() instead")]]
inline std::string to_yaml(const play_motion2_msgs::srv::GetMotionInfo_Request & msg)
{
  return play_motion2_msgs::srv::to_yaml(msg);
}

template<>
inline const char * data_type<play_motion2_msgs::srv::GetMotionInfo_Request>()
{
  return "play_motion2_msgs::srv::GetMotionInfo_Request";
}

template<>
inline const char * name<play_motion2_msgs::srv::GetMotionInfo_Request>()
{
  return "play_motion2_msgs/srv/GetMotionInfo_Request";
}

template<>
struct has_fixed_size<play_motion2_msgs::srv::GetMotionInfo_Request>
  : std::integral_constant<bool, false> {};

template<>
struct has_bounded_size<play_motion2_msgs::srv::GetMotionInfo_Request>
  : std::integral_constant<bool, false> {};

template<>
struct is_message<play_motion2_msgs::srv::GetMotionInfo_Request>
  : std::true_type {};

}  // namespace rosidl_generator_traits

// Include directives for member types
// Member 'motion'
#include "play_motion2_msgs/msg/detail/motion__traits.hpp"

namespace play_motion2_msgs
{

namespace srv
{

inline void to_flow_style_yaml(
  const GetMotionInfo_Response & msg,
  std::ostream & out)
{
  out << "{";
  // member: motion
  {
    out << "motion: ";
    to_flow_style_yaml(msg.motion, out);
  }
  out << "}";
}  // NOLINT(readability/fn_size)

inline void to_block_style_yaml(
  const GetMotionInfo_Response & msg,
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
}  // NOLINT(readability/fn_size)

inline std::string to_yaml(const GetMotionInfo_Response & msg, bool use_flow_style = false)
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
  const play_motion2_msgs::srv::GetMotionInfo_Response & msg,
  std::ostream & out, size_t indentation = 0)
{
  play_motion2_msgs::srv::to_block_style_yaml(msg, out, indentation);
}

[[deprecated("use play_motion2_msgs::srv::to_yaml() instead")]]
inline std::string to_yaml(const play_motion2_msgs::srv::GetMotionInfo_Response & msg)
{
  return play_motion2_msgs::srv::to_yaml(msg);
}

template<>
inline const char * data_type<play_motion2_msgs::srv::GetMotionInfo_Response>()
{
  return "play_motion2_msgs::srv::GetMotionInfo_Response";
}

template<>
inline const char * name<play_motion2_msgs::srv::GetMotionInfo_Response>()
{
  return "play_motion2_msgs/srv/GetMotionInfo_Response";
}

template<>
struct has_fixed_size<play_motion2_msgs::srv::GetMotionInfo_Response>
  : std::integral_constant<bool, has_fixed_size<play_motion2_msgs::msg::Motion>::value> {};

template<>
struct has_bounded_size<play_motion2_msgs::srv::GetMotionInfo_Response>
  : std::integral_constant<bool, has_bounded_size<play_motion2_msgs::msg::Motion>::value> {};

template<>
struct is_message<play_motion2_msgs::srv::GetMotionInfo_Response>
  : std::true_type {};

}  // namespace rosidl_generator_traits

namespace rosidl_generator_traits
{

template<>
inline const char * data_type<play_motion2_msgs::srv::GetMotionInfo>()
{
  return "play_motion2_msgs::srv::GetMotionInfo";
}

template<>
inline const char * name<play_motion2_msgs::srv::GetMotionInfo>()
{
  return "play_motion2_msgs/srv/GetMotionInfo";
}

template<>
struct has_fixed_size<play_motion2_msgs::srv::GetMotionInfo>
  : std::integral_constant<
    bool,
    has_fixed_size<play_motion2_msgs::srv::GetMotionInfo_Request>::value &&
    has_fixed_size<play_motion2_msgs::srv::GetMotionInfo_Response>::value
  >
{
};

template<>
struct has_bounded_size<play_motion2_msgs::srv::GetMotionInfo>
  : std::integral_constant<
    bool,
    has_bounded_size<play_motion2_msgs::srv::GetMotionInfo_Request>::value &&
    has_bounded_size<play_motion2_msgs::srv::GetMotionInfo_Response>::value
  >
{
};

template<>
struct is_service<play_motion2_msgs::srv::GetMotionInfo>
  : std::true_type
{
};

template<>
struct is_service_request<play_motion2_msgs::srv::GetMotionInfo_Request>
  : std::true_type
{
};

template<>
struct is_service_response<play_motion2_msgs::srv::GetMotionInfo_Response>
  : std::true_type
{
};

}  // namespace rosidl_generator_traits

#endif  // PLAY_MOTION2_MSGS__SRV__DETAIL__GET_MOTION_INFO__TRAITS_HPP_
