// generated from rosidl_generator_cpp/resource/idl__builder.hpp.em
// with input from play_motion2_msgs:srv/IsMotionReady.idl
// generated code does not contain a copyright notice

#ifndef PLAY_MOTION2_MSGS__SRV__DETAIL__IS_MOTION_READY__BUILDER_HPP_
#define PLAY_MOTION2_MSGS__SRV__DETAIL__IS_MOTION_READY__BUILDER_HPP_

#include <algorithm>
#include <utility>

#include "play_motion2_msgs/srv/detail/is_motion_ready__struct.hpp"
#include "rosidl_runtime_cpp/message_initialization.hpp"


namespace play_motion2_msgs
{

namespace srv
{

namespace builder
{

class Init_IsMotionReady_Request_motion_key
{
public:
  Init_IsMotionReady_Request_motion_key()
  : msg_(::rosidl_runtime_cpp::MessageInitialization::SKIP)
  {}
  ::play_motion2_msgs::srv::IsMotionReady_Request motion_key(::play_motion2_msgs::srv::IsMotionReady_Request::_motion_key_type arg)
  {
    msg_.motion_key = std::move(arg);
    return std::move(msg_);
  }

private:
  ::play_motion2_msgs::srv::IsMotionReady_Request msg_;
};

}  // namespace builder

}  // namespace srv

template<typename MessageType>
auto build();

template<>
inline
auto build<::play_motion2_msgs::srv::IsMotionReady_Request>()
{
  return play_motion2_msgs::srv::builder::Init_IsMotionReady_Request_motion_key();
}

}  // namespace play_motion2_msgs


namespace play_motion2_msgs
{

namespace srv
{

namespace builder
{

class Init_IsMotionReady_Response_is_ready
{
public:
  Init_IsMotionReady_Response_is_ready()
  : msg_(::rosidl_runtime_cpp::MessageInitialization::SKIP)
  {}
  ::play_motion2_msgs::srv::IsMotionReady_Response is_ready(::play_motion2_msgs::srv::IsMotionReady_Response::_is_ready_type arg)
  {
    msg_.is_ready = std::move(arg);
    return std::move(msg_);
  }

private:
  ::play_motion2_msgs::srv::IsMotionReady_Response msg_;
};

}  // namespace builder

}  // namespace srv

template<typename MessageType>
auto build();

template<>
inline
auto build<::play_motion2_msgs::srv::IsMotionReady_Response>()
{
  return play_motion2_msgs::srv::builder::Init_IsMotionReady_Response_is_ready();
}

}  // namespace play_motion2_msgs

#endif  // PLAY_MOTION2_MSGS__SRV__DETAIL__IS_MOTION_READY__BUILDER_HPP_
