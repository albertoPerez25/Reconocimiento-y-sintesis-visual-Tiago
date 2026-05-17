// generated from rosidl_generator_cpp/resource/idl__builder.hpp.em
// with input from hospital_interfaces:srv/GetPatrolContext.idl
// generated code does not contain a copyright notice

#ifndef HOSPITAL_INTERFACES__SRV__DETAIL__GET_PATROL_CONTEXT__BUILDER_HPP_
#define HOSPITAL_INTERFACES__SRV__DETAIL__GET_PATROL_CONTEXT__BUILDER_HPP_

#include <algorithm>
#include <utility>

#include "hospital_interfaces/srv/detail/get_patrol_context__struct.hpp"
#include "rosidl_runtime_cpp/message_initialization.hpp"


namespace hospital_interfaces
{

namespace srv
{


}  // namespace srv

template<typename MessageType>
auto build();

template<>
inline
auto build<::hospital_interfaces::srv::GetPatrolContext_Request>()
{
  return ::hospital_interfaces::srv::GetPatrolContext_Request(rosidl_runtime_cpp::MessageInitialization::ZERO);
}

}  // namespace hospital_interfaces


namespace hospital_interfaces
{

namespace srv
{

namespace builder
{

class Init_GetPatrolContext_Response_final_summary
{
public:
  explicit Init_GetPatrolContext_Response_final_summary(::hospital_interfaces::srv::GetPatrolContext_Response & msg)
  : msg_(msg)
  {}
  ::hospital_interfaces::srv::GetPatrolContext_Response final_summary(::hospital_interfaces::srv::GetPatrolContext_Response::_final_summary_type arg)
  {
    msg_.final_summary = std::move(arg);
    return std::move(msg_);
  }

private:
  ::hospital_interfaces::srv::GetPatrolContext_Response msg_;
};

class Init_GetPatrolContext_Response_global_context
{
public:
  explicit Init_GetPatrolContext_Response_global_context(::hospital_interfaces::srv::GetPatrolContext_Response & msg)
  : msg_(msg)
  {}
  Init_GetPatrolContext_Response_final_summary global_context(::hospital_interfaces::srv::GetPatrolContext_Response::_global_context_type arg)
  {
    msg_.global_context = std::move(arg);
    return Init_GetPatrolContext_Response_final_summary(msg_);
  }

private:
  ::hospital_interfaces::srv::GetPatrolContext_Response msg_;
};

class Init_GetPatrolContext_Response_success
{
public:
  Init_GetPatrolContext_Response_success()
  : msg_(::rosidl_runtime_cpp::MessageInitialization::SKIP)
  {}
  Init_GetPatrolContext_Response_global_context success(::hospital_interfaces::srv::GetPatrolContext_Response::_success_type arg)
  {
    msg_.success = std::move(arg);
    return Init_GetPatrolContext_Response_global_context(msg_);
  }

private:
  ::hospital_interfaces::srv::GetPatrolContext_Response msg_;
};

}  // namespace builder

}  // namespace srv

template<typename MessageType>
auto build();

template<>
inline
auto build<::hospital_interfaces::srv::GetPatrolContext_Response>()
{
  return hospital_interfaces::srv::builder::Init_GetPatrolContext_Response_success();
}

}  // namespace hospital_interfaces

#endif  // HOSPITAL_INTERFACES__SRV__DETAIL__GET_PATROL_CONTEXT__BUILDER_HPP_
