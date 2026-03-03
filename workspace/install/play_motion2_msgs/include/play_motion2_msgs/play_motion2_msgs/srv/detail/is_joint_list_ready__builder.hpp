// generated from rosidl_generator_cpp/resource/idl__builder.hpp.em
// with input from play_motion2_msgs:srv/IsJointListReady.idl
// generated code does not contain a copyright notice

#ifndef PLAY_MOTION2_MSGS__SRV__DETAIL__IS_JOINT_LIST_READY__BUILDER_HPP_
#define PLAY_MOTION2_MSGS__SRV__DETAIL__IS_JOINT_LIST_READY__BUILDER_HPP_

#include <algorithm>
#include <utility>

#include "play_motion2_msgs/srv/detail/is_joint_list_ready__struct.hpp"
#include "rosidl_runtime_cpp/message_initialization.hpp"


namespace play_motion2_msgs
{

namespace srv
{

namespace builder
{

class Init_IsJointListReady_Request_joints
{
public:
  Init_IsJointListReady_Request_joints()
  : msg_(::rosidl_runtime_cpp::MessageInitialization::SKIP)
  {}
  ::play_motion2_msgs::srv::IsJointListReady_Request joints(::play_motion2_msgs::srv::IsJointListReady_Request::_joints_type arg)
  {
    msg_.joints = std::move(arg);
    return std::move(msg_);
  }

private:
  ::play_motion2_msgs::srv::IsJointListReady_Request msg_;
};

}  // namespace builder

}  // namespace srv

template<typename MessageType>
auto build();

template<>
inline
auto build<::play_motion2_msgs::srv::IsJointListReady_Request>()
{
  return play_motion2_msgs::srv::builder::Init_IsJointListReady_Request_joints();
}

}  // namespace play_motion2_msgs


namespace play_motion2_msgs
{

namespace srv
{

namespace builder
{

class Init_IsJointListReady_Response_is_ready
{
public:
  Init_IsJointListReady_Response_is_ready()
  : msg_(::rosidl_runtime_cpp::MessageInitialization::SKIP)
  {}
  ::play_motion2_msgs::srv::IsJointListReady_Response is_ready(::play_motion2_msgs::srv::IsJointListReady_Response::_is_ready_type arg)
  {
    msg_.is_ready = std::move(arg);
    return std::move(msg_);
  }

private:
  ::play_motion2_msgs::srv::IsJointListReady_Response msg_;
};

}  // namespace builder

}  // namespace srv

template<typename MessageType>
auto build();

template<>
inline
auto build<::play_motion2_msgs::srv::IsJointListReady_Response>()
{
  return play_motion2_msgs::srv::builder::Init_IsJointListReady_Response_is_ready();
}

}  // namespace play_motion2_msgs

#endif  // PLAY_MOTION2_MSGS__SRV__DETAIL__IS_JOINT_LIST_READY__BUILDER_HPP_
