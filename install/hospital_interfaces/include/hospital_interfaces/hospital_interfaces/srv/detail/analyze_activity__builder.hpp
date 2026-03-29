// generated from rosidl_generator_cpp/resource/idl__builder.hpp.em
// with input from hospital_interfaces:srv/AnalyzeActivity.idl
// generated code does not contain a copyright notice

#ifndef HOSPITAL_INTERFACES__SRV__DETAIL__ANALYZE_ACTIVITY__BUILDER_HPP_
#define HOSPITAL_INTERFACES__SRV__DETAIL__ANALYZE_ACTIVITY__BUILDER_HPP_

#include <algorithm>
#include <utility>

#include "hospital_interfaces/srv/detail/analyze_activity__struct.hpp"
#include "rosidl_runtime_cpp/message_initialization.hpp"


namespace hospital_interfaces
{

namespace srv
{

namespace builder
{

class Init_AnalyzeActivity_Request_image_path
{
public:
  Init_AnalyzeActivity_Request_image_path()
  : msg_(::rosidl_runtime_cpp::MessageInitialization::SKIP)
  {}
  ::hospital_interfaces::srv::AnalyzeActivity_Request image_path(::hospital_interfaces::srv::AnalyzeActivity_Request::_image_path_type arg)
  {
    msg_.image_path = std::move(arg);
    return std::move(msg_);
  }

private:
  ::hospital_interfaces::srv::AnalyzeActivity_Request msg_;
};

}  // namespace builder

}  // namespace srv

template<typename MessageType>
auto build();

template<>
inline
auto build<::hospital_interfaces::srv::AnalyzeActivity_Request>()
{
  return hospital_interfaces::srv::builder::Init_AnalyzeActivity_Request_image_path();
}

}  // namespace hospital_interfaces


namespace hospital_interfaces
{

namespace srv
{

namespace builder
{

class Init_AnalyzeActivity_Response_report
{
public:
  Init_AnalyzeActivity_Response_report()
  : msg_(::rosidl_runtime_cpp::MessageInitialization::SKIP)
  {}
  ::hospital_interfaces::srv::AnalyzeActivity_Response report(::hospital_interfaces::srv::AnalyzeActivity_Response::_report_type arg)
  {
    msg_.report = std::move(arg);
    return std::move(msg_);
  }

private:
  ::hospital_interfaces::srv::AnalyzeActivity_Response msg_;
};

}  // namespace builder

}  // namespace srv

template<typename MessageType>
auto build();

template<>
inline
auto build<::hospital_interfaces::srv::AnalyzeActivity_Response>()
{
  return hospital_interfaces::srv::builder::Init_AnalyzeActivity_Response_report();
}

}  // namespace hospital_interfaces

#endif  // HOSPITAL_INTERFACES__SRV__DETAIL__ANALYZE_ACTIVITY__BUILDER_HPP_
