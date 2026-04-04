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

class Init_AnalyzeActivity_Request_zone_type
{
public:
  explicit Init_AnalyzeActivity_Request_zone_type(::hospital_interfaces::srv::AnalyzeActivity_Request & msg)
  : msg_(msg)
  {}
  ::hospital_interfaces::srv::AnalyzeActivity_Request zone_type(::hospital_interfaces::srv::AnalyzeActivity_Request::_zone_type_type arg)
  {
    msg_.zone_type = std::move(arg);
    return std::move(msg_);
  }

private:
  ::hospital_interfaces::srv::AnalyzeActivity_Request msg_;
};

class Init_AnalyzeActivity_Request_expected_activities
{
public:
  explicit Init_AnalyzeActivity_Request_expected_activities(::hospital_interfaces::srv::AnalyzeActivity_Request & msg)
  : msg_(msg)
  {}
  Init_AnalyzeActivity_Request_zone_type expected_activities(::hospital_interfaces::srv::AnalyzeActivity_Request::_expected_activities_type arg)
  {
    msg_.expected_activities = std::move(arg);
    return Init_AnalyzeActivity_Request_zone_type(msg_);
  }

private:
  ::hospital_interfaces::srv::AnalyzeActivity_Request msg_;
};

class Init_AnalyzeActivity_Request_time
{
public:
  explicit Init_AnalyzeActivity_Request_time(::hospital_interfaces::srv::AnalyzeActivity_Request & msg)
  : msg_(msg)
  {}
  Init_AnalyzeActivity_Request_expected_activities time(::hospital_interfaces::srv::AnalyzeActivity_Request::_time_type arg)
  {
    msg_.time = std::move(arg);
    return Init_AnalyzeActivity_Request_expected_activities(msg_);
  }

private:
  ::hospital_interfaces::srv::AnalyzeActivity_Request msg_;
};

class Init_AnalyzeActivity_Request_zone_name
{
public:
  explicit Init_AnalyzeActivity_Request_zone_name(::hospital_interfaces::srv::AnalyzeActivity_Request & msg)
  : msg_(msg)
  {}
  Init_AnalyzeActivity_Request_time zone_name(::hospital_interfaces::srv::AnalyzeActivity_Request::_zone_name_type arg)
  {
    msg_.zone_name = std::move(arg);
    return Init_AnalyzeActivity_Request_time(msg_);
  }

private:
  ::hospital_interfaces::srv::AnalyzeActivity_Request msg_;
};

class Init_AnalyzeActivity_Request_image_path
{
public:
  Init_AnalyzeActivity_Request_image_path()
  : msg_(::rosidl_runtime_cpp::MessageInitialization::SKIP)
  {}
  Init_AnalyzeActivity_Request_zone_name image_path(::hospital_interfaces::srv::AnalyzeActivity_Request::_image_path_type arg)
  {
    msg_.image_path = std::move(arg);
    return Init_AnalyzeActivity_Request_zone_name(msg_);
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
