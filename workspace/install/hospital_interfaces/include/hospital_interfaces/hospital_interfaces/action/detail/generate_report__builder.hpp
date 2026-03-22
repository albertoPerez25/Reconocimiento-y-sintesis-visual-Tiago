// generated from rosidl_generator_cpp/resource/idl__builder.hpp.em
// with input from hospital_interfaces:action/GenerateReport.idl
// generated code does not contain a copyright notice

#ifndef HOSPITAL_INTERFACES__ACTION__DETAIL__GENERATE_REPORT__BUILDER_HPP_
#define HOSPITAL_INTERFACES__ACTION__DETAIL__GENERATE_REPORT__BUILDER_HPP_

#include <algorithm>
#include <utility>

#include "hospital_interfaces/action/detail/generate_report__struct.hpp"
#include "rosidl_runtime_cpp/message_initialization.hpp"


namespace hospital_interfaces
{

namespace action
{

namespace builder
{

class Init_GenerateReport_Goal_folder_path
{
public:
  Init_GenerateReport_Goal_folder_path()
  : msg_(::rosidl_runtime_cpp::MessageInitialization::SKIP)
  {}
  ::hospital_interfaces::action::GenerateReport_Goal folder_path(::hospital_interfaces::action::GenerateReport_Goal::_folder_path_type arg)
  {
    msg_.folder_path = std::move(arg);
    return std::move(msg_);
  }

private:
  ::hospital_interfaces::action::GenerateReport_Goal msg_;
};

}  // namespace builder

}  // namespace action

template<typename MessageType>
auto build();

template<>
inline
auto build<::hospital_interfaces::action::GenerateReport_Goal>()
{
  return hospital_interfaces::action::builder::Init_GenerateReport_Goal_folder_path();
}

}  // namespace hospital_interfaces


namespace hospital_interfaces
{

namespace action
{

namespace builder
{

class Init_GenerateReport_Result_final_report
{
public:
  explicit Init_GenerateReport_Result_final_report(::hospital_interfaces::action::GenerateReport_Result & msg)
  : msg_(msg)
  {}
  ::hospital_interfaces::action::GenerateReport_Result final_report(::hospital_interfaces::action::GenerateReport_Result::_final_report_type arg)
  {
    msg_.final_report = std::move(arg);
    return std::move(msg_);
  }

private:
  ::hospital_interfaces::action::GenerateReport_Result msg_;
};

class Init_GenerateReport_Result_success
{
public:
  Init_GenerateReport_Result_success()
  : msg_(::rosidl_runtime_cpp::MessageInitialization::SKIP)
  {}
  Init_GenerateReport_Result_final_report success(::hospital_interfaces::action::GenerateReport_Result::_success_type arg)
  {
    msg_.success = std::move(arg);
    return Init_GenerateReport_Result_final_report(msg_);
  }

private:
  ::hospital_interfaces::action::GenerateReport_Result msg_;
};

}  // namespace builder

}  // namespace action

template<typename MessageType>
auto build();

template<>
inline
auto build<::hospital_interfaces::action::GenerateReport_Result>()
{
  return hospital_interfaces::action::builder::Init_GenerateReport_Result_success();
}

}  // namespace hospital_interfaces


namespace hospital_interfaces
{

namespace action
{

namespace builder
{

class Init_GenerateReport_Feedback_percentage_complete
{
public:
  explicit Init_GenerateReport_Feedback_percentage_complete(::hospital_interfaces::action::GenerateReport_Feedback & msg)
  : msg_(msg)
  {}
  ::hospital_interfaces::action::GenerateReport_Feedback percentage_complete(::hospital_interfaces::action::GenerateReport_Feedback::_percentage_complete_type arg)
  {
    msg_.percentage_complete = std::move(arg);
    return std::move(msg_);
  }

private:
  ::hospital_interfaces::action::GenerateReport_Feedback msg_;
};

class Init_GenerateReport_Feedback_current_zone
{
public:
  Init_GenerateReport_Feedback_current_zone()
  : msg_(::rosidl_runtime_cpp::MessageInitialization::SKIP)
  {}
  Init_GenerateReport_Feedback_percentage_complete current_zone(::hospital_interfaces::action::GenerateReport_Feedback::_current_zone_type arg)
  {
    msg_.current_zone = std::move(arg);
    return Init_GenerateReport_Feedback_percentage_complete(msg_);
  }

private:
  ::hospital_interfaces::action::GenerateReport_Feedback msg_;
};

}  // namespace builder

}  // namespace action

template<typename MessageType>
auto build();

template<>
inline
auto build<::hospital_interfaces::action::GenerateReport_Feedback>()
{
  return hospital_interfaces::action::builder::Init_GenerateReport_Feedback_current_zone();
}

}  // namespace hospital_interfaces


namespace hospital_interfaces
{

namespace action
{

namespace builder
{

class Init_GenerateReport_SendGoal_Request_goal
{
public:
  explicit Init_GenerateReport_SendGoal_Request_goal(::hospital_interfaces::action::GenerateReport_SendGoal_Request & msg)
  : msg_(msg)
  {}
  ::hospital_interfaces::action::GenerateReport_SendGoal_Request goal(::hospital_interfaces::action::GenerateReport_SendGoal_Request::_goal_type arg)
  {
    msg_.goal = std::move(arg);
    return std::move(msg_);
  }

private:
  ::hospital_interfaces::action::GenerateReport_SendGoal_Request msg_;
};

class Init_GenerateReport_SendGoal_Request_goal_id
{
public:
  Init_GenerateReport_SendGoal_Request_goal_id()
  : msg_(::rosidl_runtime_cpp::MessageInitialization::SKIP)
  {}
  Init_GenerateReport_SendGoal_Request_goal goal_id(::hospital_interfaces::action::GenerateReport_SendGoal_Request::_goal_id_type arg)
  {
    msg_.goal_id = std::move(arg);
    return Init_GenerateReport_SendGoal_Request_goal(msg_);
  }

private:
  ::hospital_interfaces::action::GenerateReport_SendGoal_Request msg_;
};

}  // namespace builder

}  // namespace action

template<typename MessageType>
auto build();

template<>
inline
auto build<::hospital_interfaces::action::GenerateReport_SendGoal_Request>()
{
  return hospital_interfaces::action::builder::Init_GenerateReport_SendGoal_Request_goal_id();
}

}  // namespace hospital_interfaces


namespace hospital_interfaces
{

namespace action
{

namespace builder
{

class Init_GenerateReport_SendGoal_Response_stamp
{
public:
  explicit Init_GenerateReport_SendGoal_Response_stamp(::hospital_interfaces::action::GenerateReport_SendGoal_Response & msg)
  : msg_(msg)
  {}
  ::hospital_interfaces::action::GenerateReport_SendGoal_Response stamp(::hospital_interfaces::action::GenerateReport_SendGoal_Response::_stamp_type arg)
  {
    msg_.stamp = std::move(arg);
    return std::move(msg_);
  }

private:
  ::hospital_interfaces::action::GenerateReport_SendGoal_Response msg_;
};

class Init_GenerateReport_SendGoal_Response_accepted
{
public:
  Init_GenerateReport_SendGoal_Response_accepted()
  : msg_(::rosidl_runtime_cpp::MessageInitialization::SKIP)
  {}
  Init_GenerateReport_SendGoal_Response_stamp accepted(::hospital_interfaces::action::GenerateReport_SendGoal_Response::_accepted_type arg)
  {
    msg_.accepted = std::move(arg);
    return Init_GenerateReport_SendGoal_Response_stamp(msg_);
  }

private:
  ::hospital_interfaces::action::GenerateReport_SendGoal_Response msg_;
};

}  // namespace builder

}  // namespace action

template<typename MessageType>
auto build();

template<>
inline
auto build<::hospital_interfaces::action::GenerateReport_SendGoal_Response>()
{
  return hospital_interfaces::action::builder::Init_GenerateReport_SendGoal_Response_accepted();
}

}  // namespace hospital_interfaces


namespace hospital_interfaces
{

namespace action
{

namespace builder
{

class Init_GenerateReport_GetResult_Request_goal_id
{
public:
  Init_GenerateReport_GetResult_Request_goal_id()
  : msg_(::rosidl_runtime_cpp::MessageInitialization::SKIP)
  {}
  ::hospital_interfaces::action::GenerateReport_GetResult_Request goal_id(::hospital_interfaces::action::GenerateReport_GetResult_Request::_goal_id_type arg)
  {
    msg_.goal_id = std::move(arg);
    return std::move(msg_);
  }

private:
  ::hospital_interfaces::action::GenerateReport_GetResult_Request msg_;
};

}  // namespace builder

}  // namespace action

template<typename MessageType>
auto build();

template<>
inline
auto build<::hospital_interfaces::action::GenerateReport_GetResult_Request>()
{
  return hospital_interfaces::action::builder::Init_GenerateReport_GetResult_Request_goal_id();
}

}  // namespace hospital_interfaces


namespace hospital_interfaces
{

namespace action
{

namespace builder
{

class Init_GenerateReport_GetResult_Response_result
{
public:
  explicit Init_GenerateReport_GetResult_Response_result(::hospital_interfaces::action::GenerateReport_GetResult_Response & msg)
  : msg_(msg)
  {}
  ::hospital_interfaces::action::GenerateReport_GetResult_Response result(::hospital_interfaces::action::GenerateReport_GetResult_Response::_result_type arg)
  {
    msg_.result = std::move(arg);
    return std::move(msg_);
  }

private:
  ::hospital_interfaces::action::GenerateReport_GetResult_Response msg_;
};

class Init_GenerateReport_GetResult_Response_status
{
public:
  Init_GenerateReport_GetResult_Response_status()
  : msg_(::rosidl_runtime_cpp::MessageInitialization::SKIP)
  {}
  Init_GenerateReport_GetResult_Response_result status(::hospital_interfaces::action::GenerateReport_GetResult_Response::_status_type arg)
  {
    msg_.status = std::move(arg);
    return Init_GenerateReport_GetResult_Response_result(msg_);
  }

private:
  ::hospital_interfaces::action::GenerateReport_GetResult_Response msg_;
};

}  // namespace builder

}  // namespace action

template<typename MessageType>
auto build();

template<>
inline
auto build<::hospital_interfaces::action::GenerateReport_GetResult_Response>()
{
  return hospital_interfaces::action::builder::Init_GenerateReport_GetResult_Response_status();
}

}  // namespace hospital_interfaces


namespace hospital_interfaces
{

namespace action
{

namespace builder
{

class Init_GenerateReport_FeedbackMessage_feedback
{
public:
  explicit Init_GenerateReport_FeedbackMessage_feedback(::hospital_interfaces::action::GenerateReport_FeedbackMessage & msg)
  : msg_(msg)
  {}
  ::hospital_interfaces::action::GenerateReport_FeedbackMessage feedback(::hospital_interfaces::action::GenerateReport_FeedbackMessage::_feedback_type arg)
  {
    msg_.feedback = std::move(arg);
    return std::move(msg_);
  }

private:
  ::hospital_interfaces::action::GenerateReport_FeedbackMessage msg_;
};

class Init_GenerateReport_FeedbackMessage_goal_id
{
public:
  Init_GenerateReport_FeedbackMessage_goal_id()
  : msg_(::rosidl_runtime_cpp::MessageInitialization::SKIP)
  {}
  Init_GenerateReport_FeedbackMessage_feedback goal_id(::hospital_interfaces::action::GenerateReport_FeedbackMessage::_goal_id_type arg)
  {
    msg_.goal_id = std::move(arg);
    return Init_GenerateReport_FeedbackMessage_feedback(msg_);
  }

private:
  ::hospital_interfaces::action::GenerateReport_FeedbackMessage msg_;
};

}  // namespace builder

}  // namespace action

template<typename MessageType>
auto build();

template<>
inline
auto build<::hospital_interfaces::action::GenerateReport_FeedbackMessage>()
{
  return hospital_interfaces::action::builder::Init_GenerateReport_FeedbackMessage_goal_id();
}

}  // namespace hospital_interfaces

#endif  // HOSPITAL_INTERFACES__ACTION__DETAIL__GENERATE_REPORT__BUILDER_HPP_
