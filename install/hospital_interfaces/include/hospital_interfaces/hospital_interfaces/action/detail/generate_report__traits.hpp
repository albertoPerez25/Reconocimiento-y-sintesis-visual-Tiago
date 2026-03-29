// generated from rosidl_generator_cpp/resource/idl__traits.hpp.em
// with input from hospital_interfaces:action/GenerateReport.idl
// generated code does not contain a copyright notice

#ifndef HOSPITAL_INTERFACES__ACTION__DETAIL__GENERATE_REPORT__TRAITS_HPP_
#define HOSPITAL_INTERFACES__ACTION__DETAIL__GENERATE_REPORT__TRAITS_HPP_

#include <stdint.h>

#include <sstream>
#include <string>
#include <type_traits>

#include "hospital_interfaces/action/detail/generate_report__struct.hpp"
#include "rosidl_runtime_cpp/traits.hpp"

namespace hospital_interfaces
{

namespace action
{

inline void to_flow_style_yaml(
  const GenerateReport_Goal & msg,
  std::ostream & out)
{
  out << "{";
  // member: folder_path
  {
    out << "folder_path: ";
    rosidl_generator_traits::value_to_yaml(msg.folder_path, out);
  }
  out << "}";
}  // NOLINT(readability/fn_size)

inline void to_block_style_yaml(
  const GenerateReport_Goal & msg,
  std::ostream & out, size_t indentation = 0)
{
  // member: folder_path
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "folder_path: ";
    rosidl_generator_traits::value_to_yaml(msg.folder_path, out);
    out << "\n";
  }
}  // NOLINT(readability/fn_size)

inline std::string to_yaml(const GenerateReport_Goal & msg, bool use_flow_style = false)
{
  std::ostringstream out;
  if (use_flow_style) {
    to_flow_style_yaml(msg, out);
  } else {
    to_block_style_yaml(msg, out);
  }
  return out.str();
}

}  // namespace action

}  // namespace hospital_interfaces

namespace rosidl_generator_traits
{

[[deprecated("use hospital_interfaces::action::to_block_style_yaml() instead")]]
inline void to_yaml(
  const hospital_interfaces::action::GenerateReport_Goal & msg,
  std::ostream & out, size_t indentation = 0)
{
  hospital_interfaces::action::to_block_style_yaml(msg, out, indentation);
}

[[deprecated("use hospital_interfaces::action::to_yaml() instead")]]
inline std::string to_yaml(const hospital_interfaces::action::GenerateReport_Goal & msg)
{
  return hospital_interfaces::action::to_yaml(msg);
}

template<>
inline const char * data_type<hospital_interfaces::action::GenerateReport_Goal>()
{
  return "hospital_interfaces::action::GenerateReport_Goal";
}

template<>
inline const char * name<hospital_interfaces::action::GenerateReport_Goal>()
{
  return "hospital_interfaces/action/GenerateReport_Goal";
}

template<>
struct has_fixed_size<hospital_interfaces::action::GenerateReport_Goal>
  : std::integral_constant<bool, false> {};

template<>
struct has_bounded_size<hospital_interfaces::action::GenerateReport_Goal>
  : std::integral_constant<bool, false> {};

template<>
struct is_message<hospital_interfaces::action::GenerateReport_Goal>
  : std::true_type {};

}  // namespace rosidl_generator_traits

namespace hospital_interfaces
{

namespace action
{

inline void to_flow_style_yaml(
  const GenerateReport_Result & msg,
  std::ostream & out)
{
  out << "{";
  // member: success
  {
    out << "success: ";
    rosidl_generator_traits::value_to_yaml(msg.success, out);
    out << ", ";
  }

  // member: final_report
  {
    out << "final_report: ";
    rosidl_generator_traits::value_to_yaml(msg.final_report, out);
  }
  out << "}";
}  // NOLINT(readability/fn_size)

inline void to_block_style_yaml(
  const GenerateReport_Result & msg,
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

  // member: final_report
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "final_report: ";
    rosidl_generator_traits::value_to_yaml(msg.final_report, out);
    out << "\n";
  }
}  // NOLINT(readability/fn_size)

inline std::string to_yaml(const GenerateReport_Result & msg, bool use_flow_style = false)
{
  std::ostringstream out;
  if (use_flow_style) {
    to_flow_style_yaml(msg, out);
  } else {
    to_block_style_yaml(msg, out);
  }
  return out.str();
}

}  // namespace action

}  // namespace hospital_interfaces

namespace rosidl_generator_traits
{

[[deprecated("use hospital_interfaces::action::to_block_style_yaml() instead")]]
inline void to_yaml(
  const hospital_interfaces::action::GenerateReport_Result & msg,
  std::ostream & out, size_t indentation = 0)
{
  hospital_interfaces::action::to_block_style_yaml(msg, out, indentation);
}

[[deprecated("use hospital_interfaces::action::to_yaml() instead")]]
inline std::string to_yaml(const hospital_interfaces::action::GenerateReport_Result & msg)
{
  return hospital_interfaces::action::to_yaml(msg);
}

template<>
inline const char * data_type<hospital_interfaces::action::GenerateReport_Result>()
{
  return "hospital_interfaces::action::GenerateReport_Result";
}

template<>
inline const char * name<hospital_interfaces::action::GenerateReport_Result>()
{
  return "hospital_interfaces/action/GenerateReport_Result";
}

template<>
struct has_fixed_size<hospital_interfaces::action::GenerateReport_Result>
  : std::integral_constant<bool, false> {};

template<>
struct has_bounded_size<hospital_interfaces::action::GenerateReport_Result>
  : std::integral_constant<bool, false> {};

template<>
struct is_message<hospital_interfaces::action::GenerateReport_Result>
  : std::true_type {};

}  // namespace rosidl_generator_traits

namespace hospital_interfaces
{

namespace action
{

inline void to_flow_style_yaml(
  const GenerateReport_Feedback & msg,
  std::ostream & out)
{
  out << "{";
  // member: current_zone
  {
    out << "current_zone: ";
    rosidl_generator_traits::value_to_yaml(msg.current_zone, out);
    out << ", ";
  }

  // member: percentage_complete
  {
    out << "percentage_complete: ";
    rosidl_generator_traits::value_to_yaml(msg.percentage_complete, out);
  }
  out << "}";
}  // NOLINT(readability/fn_size)

inline void to_block_style_yaml(
  const GenerateReport_Feedback & msg,
  std::ostream & out, size_t indentation = 0)
{
  // member: current_zone
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "current_zone: ";
    rosidl_generator_traits::value_to_yaml(msg.current_zone, out);
    out << "\n";
  }

  // member: percentage_complete
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "percentage_complete: ";
    rosidl_generator_traits::value_to_yaml(msg.percentage_complete, out);
    out << "\n";
  }
}  // NOLINT(readability/fn_size)

inline std::string to_yaml(const GenerateReport_Feedback & msg, bool use_flow_style = false)
{
  std::ostringstream out;
  if (use_flow_style) {
    to_flow_style_yaml(msg, out);
  } else {
    to_block_style_yaml(msg, out);
  }
  return out.str();
}

}  // namespace action

}  // namespace hospital_interfaces

namespace rosidl_generator_traits
{

[[deprecated("use hospital_interfaces::action::to_block_style_yaml() instead")]]
inline void to_yaml(
  const hospital_interfaces::action::GenerateReport_Feedback & msg,
  std::ostream & out, size_t indentation = 0)
{
  hospital_interfaces::action::to_block_style_yaml(msg, out, indentation);
}

[[deprecated("use hospital_interfaces::action::to_yaml() instead")]]
inline std::string to_yaml(const hospital_interfaces::action::GenerateReport_Feedback & msg)
{
  return hospital_interfaces::action::to_yaml(msg);
}

template<>
inline const char * data_type<hospital_interfaces::action::GenerateReport_Feedback>()
{
  return "hospital_interfaces::action::GenerateReport_Feedback";
}

template<>
inline const char * name<hospital_interfaces::action::GenerateReport_Feedback>()
{
  return "hospital_interfaces/action/GenerateReport_Feedback";
}

template<>
struct has_fixed_size<hospital_interfaces::action::GenerateReport_Feedback>
  : std::integral_constant<bool, false> {};

template<>
struct has_bounded_size<hospital_interfaces::action::GenerateReport_Feedback>
  : std::integral_constant<bool, false> {};

template<>
struct is_message<hospital_interfaces::action::GenerateReport_Feedback>
  : std::true_type {};

}  // namespace rosidl_generator_traits

// Include directives for member types
// Member 'goal_id'
#include "unique_identifier_msgs/msg/detail/uuid__traits.hpp"
// Member 'goal'
#include "hospital_interfaces/action/detail/generate_report__traits.hpp"

namespace hospital_interfaces
{

namespace action
{

inline void to_flow_style_yaml(
  const GenerateReport_SendGoal_Request & msg,
  std::ostream & out)
{
  out << "{";
  // member: goal_id
  {
    out << "goal_id: ";
    to_flow_style_yaml(msg.goal_id, out);
    out << ", ";
  }

  // member: goal
  {
    out << "goal: ";
    to_flow_style_yaml(msg.goal, out);
  }
  out << "}";
}  // NOLINT(readability/fn_size)

inline void to_block_style_yaml(
  const GenerateReport_SendGoal_Request & msg,
  std::ostream & out, size_t indentation = 0)
{
  // member: goal_id
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "goal_id:\n";
    to_block_style_yaml(msg.goal_id, out, indentation + 2);
  }

  // member: goal
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "goal:\n";
    to_block_style_yaml(msg.goal, out, indentation + 2);
  }
}  // NOLINT(readability/fn_size)

inline std::string to_yaml(const GenerateReport_SendGoal_Request & msg, bool use_flow_style = false)
{
  std::ostringstream out;
  if (use_flow_style) {
    to_flow_style_yaml(msg, out);
  } else {
    to_block_style_yaml(msg, out);
  }
  return out.str();
}

}  // namespace action

}  // namespace hospital_interfaces

namespace rosidl_generator_traits
{

[[deprecated("use hospital_interfaces::action::to_block_style_yaml() instead")]]
inline void to_yaml(
  const hospital_interfaces::action::GenerateReport_SendGoal_Request & msg,
  std::ostream & out, size_t indentation = 0)
{
  hospital_interfaces::action::to_block_style_yaml(msg, out, indentation);
}

[[deprecated("use hospital_interfaces::action::to_yaml() instead")]]
inline std::string to_yaml(const hospital_interfaces::action::GenerateReport_SendGoal_Request & msg)
{
  return hospital_interfaces::action::to_yaml(msg);
}

template<>
inline const char * data_type<hospital_interfaces::action::GenerateReport_SendGoal_Request>()
{
  return "hospital_interfaces::action::GenerateReport_SendGoal_Request";
}

template<>
inline const char * name<hospital_interfaces::action::GenerateReport_SendGoal_Request>()
{
  return "hospital_interfaces/action/GenerateReport_SendGoal_Request";
}

template<>
struct has_fixed_size<hospital_interfaces::action::GenerateReport_SendGoal_Request>
  : std::integral_constant<bool, has_fixed_size<hospital_interfaces::action::GenerateReport_Goal>::value && has_fixed_size<unique_identifier_msgs::msg::UUID>::value> {};

template<>
struct has_bounded_size<hospital_interfaces::action::GenerateReport_SendGoal_Request>
  : std::integral_constant<bool, has_bounded_size<hospital_interfaces::action::GenerateReport_Goal>::value && has_bounded_size<unique_identifier_msgs::msg::UUID>::value> {};

template<>
struct is_message<hospital_interfaces::action::GenerateReport_SendGoal_Request>
  : std::true_type {};

}  // namespace rosidl_generator_traits

// Include directives for member types
// Member 'stamp'
#include "builtin_interfaces/msg/detail/time__traits.hpp"

namespace hospital_interfaces
{

namespace action
{

inline void to_flow_style_yaml(
  const GenerateReport_SendGoal_Response & msg,
  std::ostream & out)
{
  out << "{";
  // member: accepted
  {
    out << "accepted: ";
    rosidl_generator_traits::value_to_yaml(msg.accepted, out);
    out << ", ";
  }

  // member: stamp
  {
    out << "stamp: ";
    to_flow_style_yaml(msg.stamp, out);
  }
  out << "}";
}  // NOLINT(readability/fn_size)

inline void to_block_style_yaml(
  const GenerateReport_SendGoal_Response & msg,
  std::ostream & out, size_t indentation = 0)
{
  // member: accepted
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "accepted: ";
    rosidl_generator_traits::value_to_yaml(msg.accepted, out);
    out << "\n";
  }

  // member: stamp
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "stamp:\n";
    to_block_style_yaml(msg.stamp, out, indentation + 2);
  }
}  // NOLINT(readability/fn_size)

inline std::string to_yaml(const GenerateReport_SendGoal_Response & msg, bool use_flow_style = false)
{
  std::ostringstream out;
  if (use_flow_style) {
    to_flow_style_yaml(msg, out);
  } else {
    to_block_style_yaml(msg, out);
  }
  return out.str();
}

}  // namespace action

}  // namespace hospital_interfaces

namespace rosidl_generator_traits
{

[[deprecated("use hospital_interfaces::action::to_block_style_yaml() instead")]]
inline void to_yaml(
  const hospital_interfaces::action::GenerateReport_SendGoal_Response & msg,
  std::ostream & out, size_t indentation = 0)
{
  hospital_interfaces::action::to_block_style_yaml(msg, out, indentation);
}

[[deprecated("use hospital_interfaces::action::to_yaml() instead")]]
inline std::string to_yaml(const hospital_interfaces::action::GenerateReport_SendGoal_Response & msg)
{
  return hospital_interfaces::action::to_yaml(msg);
}

template<>
inline const char * data_type<hospital_interfaces::action::GenerateReport_SendGoal_Response>()
{
  return "hospital_interfaces::action::GenerateReport_SendGoal_Response";
}

template<>
inline const char * name<hospital_interfaces::action::GenerateReport_SendGoal_Response>()
{
  return "hospital_interfaces/action/GenerateReport_SendGoal_Response";
}

template<>
struct has_fixed_size<hospital_interfaces::action::GenerateReport_SendGoal_Response>
  : std::integral_constant<bool, has_fixed_size<builtin_interfaces::msg::Time>::value> {};

template<>
struct has_bounded_size<hospital_interfaces::action::GenerateReport_SendGoal_Response>
  : std::integral_constant<bool, has_bounded_size<builtin_interfaces::msg::Time>::value> {};

template<>
struct is_message<hospital_interfaces::action::GenerateReport_SendGoal_Response>
  : std::true_type {};

}  // namespace rosidl_generator_traits

namespace rosidl_generator_traits
{

template<>
inline const char * data_type<hospital_interfaces::action::GenerateReport_SendGoal>()
{
  return "hospital_interfaces::action::GenerateReport_SendGoal";
}

template<>
inline const char * name<hospital_interfaces::action::GenerateReport_SendGoal>()
{
  return "hospital_interfaces/action/GenerateReport_SendGoal";
}

template<>
struct has_fixed_size<hospital_interfaces::action::GenerateReport_SendGoal>
  : std::integral_constant<
    bool,
    has_fixed_size<hospital_interfaces::action::GenerateReport_SendGoal_Request>::value &&
    has_fixed_size<hospital_interfaces::action::GenerateReport_SendGoal_Response>::value
  >
{
};

template<>
struct has_bounded_size<hospital_interfaces::action::GenerateReport_SendGoal>
  : std::integral_constant<
    bool,
    has_bounded_size<hospital_interfaces::action::GenerateReport_SendGoal_Request>::value &&
    has_bounded_size<hospital_interfaces::action::GenerateReport_SendGoal_Response>::value
  >
{
};

template<>
struct is_service<hospital_interfaces::action::GenerateReport_SendGoal>
  : std::true_type
{
};

template<>
struct is_service_request<hospital_interfaces::action::GenerateReport_SendGoal_Request>
  : std::true_type
{
};

template<>
struct is_service_response<hospital_interfaces::action::GenerateReport_SendGoal_Response>
  : std::true_type
{
};

}  // namespace rosidl_generator_traits

// Include directives for member types
// Member 'goal_id'
// already included above
// #include "unique_identifier_msgs/msg/detail/uuid__traits.hpp"

namespace hospital_interfaces
{

namespace action
{

inline void to_flow_style_yaml(
  const GenerateReport_GetResult_Request & msg,
  std::ostream & out)
{
  out << "{";
  // member: goal_id
  {
    out << "goal_id: ";
    to_flow_style_yaml(msg.goal_id, out);
  }
  out << "}";
}  // NOLINT(readability/fn_size)

inline void to_block_style_yaml(
  const GenerateReport_GetResult_Request & msg,
  std::ostream & out, size_t indentation = 0)
{
  // member: goal_id
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "goal_id:\n";
    to_block_style_yaml(msg.goal_id, out, indentation + 2);
  }
}  // NOLINT(readability/fn_size)

inline std::string to_yaml(const GenerateReport_GetResult_Request & msg, bool use_flow_style = false)
{
  std::ostringstream out;
  if (use_flow_style) {
    to_flow_style_yaml(msg, out);
  } else {
    to_block_style_yaml(msg, out);
  }
  return out.str();
}

}  // namespace action

}  // namespace hospital_interfaces

namespace rosidl_generator_traits
{

[[deprecated("use hospital_interfaces::action::to_block_style_yaml() instead")]]
inline void to_yaml(
  const hospital_interfaces::action::GenerateReport_GetResult_Request & msg,
  std::ostream & out, size_t indentation = 0)
{
  hospital_interfaces::action::to_block_style_yaml(msg, out, indentation);
}

[[deprecated("use hospital_interfaces::action::to_yaml() instead")]]
inline std::string to_yaml(const hospital_interfaces::action::GenerateReport_GetResult_Request & msg)
{
  return hospital_interfaces::action::to_yaml(msg);
}

template<>
inline const char * data_type<hospital_interfaces::action::GenerateReport_GetResult_Request>()
{
  return "hospital_interfaces::action::GenerateReport_GetResult_Request";
}

template<>
inline const char * name<hospital_interfaces::action::GenerateReport_GetResult_Request>()
{
  return "hospital_interfaces/action/GenerateReport_GetResult_Request";
}

template<>
struct has_fixed_size<hospital_interfaces::action::GenerateReport_GetResult_Request>
  : std::integral_constant<bool, has_fixed_size<unique_identifier_msgs::msg::UUID>::value> {};

template<>
struct has_bounded_size<hospital_interfaces::action::GenerateReport_GetResult_Request>
  : std::integral_constant<bool, has_bounded_size<unique_identifier_msgs::msg::UUID>::value> {};

template<>
struct is_message<hospital_interfaces::action::GenerateReport_GetResult_Request>
  : std::true_type {};

}  // namespace rosidl_generator_traits

// Include directives for member types
// Member 'result'
// already included above
// #include "hospital_interfaces/action/detail/generate_report__traits.hpp"

namespace hospital_interfaces
{

namespace action
{

inline void to_flow_style_yaml(
  const GenerateReport_GetResult_Response & msg,
  std::ostream & out)
{
  out << "{";
  // member: status
  {
    out << "status: ";
    rosidl_generator_traits::value_to_yaml(msg.status, out);
    out << ", ";
  }

  // member: result
  {
    out << "result: ";
    to_flow_style_yaml(msg.result, out);
  }
  out << "}";
}  // NOLINT(readability/fn_size)

inline void to_block_style_yaml(
  const GenerateReport_GetResult_Response & msg,
  std::ostream & out, size_t indentation = 0)
{
  // member: status
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "status: ";
    rosidl_generator_traits::value_to_yaml(msg.status, out);
    out << "\n";
  }

  // member: result
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "result:\n";
    to_block_style_yaml(msg.result, out, indentation + 2);
  }
}  // NOLINT(readability/fn_size)

inline std::string to_yaml(const GenerateReport_GetResult_Response & msg, bool use_flow_style = false)
{
  std::ostringstream out;
  if (use_flow_style) {
    to_flow_style_yaml(msg, out);
  } else {
    to_block_style_yaml(msg, out);
  }
  return out.str();
}

}  // namespace action

}  // namespace hospital_interfaces

namespace rosidl_generator_traits
{

[[deprecated("use hospital_interfaces::action::to_block_style_yaml() instead")]]
inline void to_yaml(
  const hospital_interfaces::action::GenerateReport_GetResult_Response & msg,
  std::ostream & out, size_t indentation = 0)
{
  hospital_interfaces::action::to_block_style_yaml(msg, out, indentation);
}

[[deprecated("use hospital_interfaces::action::to_yaml() instead")]]
inline std::string to_yaml(const hospital_interfaces::action::GenerateReport_GetResult_Response & msg)
{
  return hospital_interfaces::action::to_yaml(msg);
}

template<>
inline const char * data_type<hospital_interfaces::action::GenerateReport_GetResult_Response>()
{
  return "hospital_interfaces::action::GenerateReport_GetResult_Response";
}

template<>
inline const char * name<hospital_interfaces::action::GenerateReport_GetResult_Response>()
{
  return "hospital_interfaces/action/GenerateReport_GetResult_Response";
}

template<>
struct has_fixed_size<hospital_interfaces::action::GenerateReport_GetResult_Response>
  : std::integral_constant<bool, has_fixed_size<hospital_interfaces::action::GenerateReport_Result>::value> {};

template<>
struct has_bounded_size<hospital_interfaces::action::GenerateReport_GetResult_Response>
  : std::integral_constant<bool, has_bounded_size<hospital_interfaces::action::GenerateReport_Result>::value> {};

template<>
struct is_message<hospital_interfaces::action::GenerateReport_GetResult_Response>
  : std::true_type {};

}  // namespace rosidl_generator_traits

namespace rosidl_generator_traits
{

template<>
inline const char * data_type<hospital_interfaces::action::GenerateReport_GetResult>()
{
  return "hospital_interfaces::action::GenerateReport_GetResult";
}

template<>
inline const char * name<hospital_interfaces::action::GenerateReport_GetResult>()
{
  return "hospital_interfaces/action/GenerateReport_GetResult";
}

template<>
struct has_fixed_size<hospital_interfaces::action::GenerateReport_GetResult>
  : std::integral_constant<
    bool,
    has_fixed_size<hospital_interfaces::action::GenerateReport_GetResult_Request>::value &&
    has_fixed_size<hospital_interfaces::action::GenerateReport_GetResult_Response>::value
  >
{
};

template<>
struct has_bounded_size<hospital_interfaces::action::GenerateReport_GetResult>
  : std::integral_constant<
    bool,
    has_bounded_size<hospital_interfaces::action::GenerateReport_GetResult_Request>::value &&
    has_bounded_size<hospital_interfaces::action::GenerateReport_GetResult_Response>::value
  >
{
};

template<>
struct is_service<hospital_interfaces::action::GenerateReport_GetResult>
  : std::true_type
{
};

template<>
struct is_service_request<hospital_interfaces::action::GenerateReport_GetResult_Request>
  : std::true_type
{
};

template<>
struct is_service_response<hospital_interfaces::action::GenerateReport_GetResult_Response>
  : std::true_type
{
};

}  // namespace rosidl_generator_traits

// Include directives for member types
// Member 'goal_id'
// already included above
// #include "unique_identifier_msgs/msg/detail/uuid__traits.hpp"
// Member 'feedback'
// already included above
// #include "hospital_interfaces/action/detail/generate_report__traits.hpp"

namespace hospital_interfaces
{

namespace action
{

inline void to_flow_style_yaml(
  const GenerateReport_FeedbackMessage & msg,
  std::ostream & out)
{
  out << "{";
  // member: goal_id
  {
    out << "goal_id: ";
    to_flow_style_yaml(msg.goal_id, out);
    out << ", ";
  }

  // member: feedback
  {
    out << "feedback: ";
    to_flow_style_yaml(msg.feedback, out);
  }
  out << "}";
}  // NOLINT(readability/fn_size)

inline void to_block_style_yaml(
  const GenerateReport_FeedbackMessage & msg,
  std::ostream & out, size_t indentation = 0)
{
  // member: goal_id
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "goal_id:\n";
    to_block_style_yaml(msg.goal_id, out, indentation + 2);
  }

  // member: feedback
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "feedback:\n";
    to_block_style_yaml(msg.feedback, out, indentation + 2);
  }
}  // NOLINT(readability/fn_size)

inline std::string to_yaml(const GenerateReport_FeedbackMessage & msg, bool use_flow_style = false)
{
  std::ostringstream out;
  if (use_flow_style) {
    to_flow_style_yaml(msg, out);
  } else {
    to_block_style_yaml(msg, out);
  }
  return out.str();
}

}  // namespace action

}  // namespace hospital_interfaces

namespace rosidl_generator_traits
{

[[deprecated("use hospital_interfaces::action::to_block_style_yaml() instead")]]
inline void to_yaml(
  const hospital_interfaces::action::GenerateReport_FeedbackMessage & msg,
  std::ostream & out, size_t indentation = 0)
{
  hospital_interfaces::action::to_block_style_yaml(msg, out, indentation);
}

[[deprecated("use hospital_interfaces::action::to_yaml() instead")]]
inline std::string to_yaml(const hospital_interfaces::action::GenerateReport_FeedbackMessage & msg)
{
  return hospital_interfaces::action::to_yaml(msg);
}

template<>
inline const char * data_type<hospital_interfaces::action::GenerateReport_FeedbackMessage>()
{
  return "hospital_interfaces::action::GenerateReport_FeedbackMessage";
}

template<>
inline const char * name<hospital_interfaces::action::GenerateReport_FeedbackMessage>()
{
  return "hospital_interfaces/action/GenerateReport_FeedbackMessage";
}

template<>
struct has_fixed_size<hospital_interfaces::action::GenerateReport_FeedbackMessage>
  : std::integral_constant<bool, has_fixed_size<hospital_interfaces::action::GenerateReport_Feedback>::value && has_fixed_size<unique_identifier_msgs::msg::UUID>::value> {};

template<>
struct has_bounded_size<hospital_interfaces::action::GenerateReport_FeedbackMessage>
  : std::integral_constant<bool, has_bounded_size<hospital_interfaces::action::GenerateReport_Feedback>::value && has_bounded_size<unique_identifier_msgs::msg::UUID>::value> {};

template<>
struct is_message<hospital_interfaces::action::GenerateReport_FeedbackMessage>
  : std::true_type {};

}  // namespace rosidl_generator_traits


namespace rosidl_generator_traits
{

template<>
struct is_action<hospital_interfaces::action::GenerateReport>
  : std::true_type
{
};

template<>
struct is_action_goal<hospital_interfaces::action::GenerateReport_Goal>
  : std::true_type
{
};

template<>
struct is_action_result<hospital_interfaces::action::GenerateReport_Result>
  : std::true_type
{
};

template<>
struct is_action_feedback<hospital_interfaces::action::GenerateReport_Feedback>
  : std::true_type
{
};

}  // namespace rosidl_generator_traits


#endif  // HOSPITAL_INTERFACES__ACTION__DETAIL__GENERATE_REPORT__TRAITS_HPP_
