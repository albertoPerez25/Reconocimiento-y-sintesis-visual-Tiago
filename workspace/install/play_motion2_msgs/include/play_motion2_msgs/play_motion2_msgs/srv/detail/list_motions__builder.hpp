// generated from rosidl_generator_cpp/resource/idl__builder.hpp.em
// with input from play_motion2_msgs:srv/ListMotions.idl
// generated code does not contain a copyright notice

#ifndef PLAY_MOTION2_MSGS__SRV__DETAIL__LIST_MOTIONS__BUILDER_HPP_
#define PLAY_MOTION2_MSGS__SRV__DETAIL__LIST_MOTIONS__BUILDER_HPP_

#include <algorithm>
#include <utility>

#include "play_motion2_msgs/srv/detail/list_motions__struct.hpp"
#include "rosidl_runtime_cpp/message_initialization.hpp"


namespace play_motion2_msgs
{

namespace srv
{


}  // namespace srv

template<typename MessageType>
auto build();

template<>
inline
auto build<::play_motion2_msgs::srv::ListMotions_Request>()
{
  return ::play_motion2_msgs::srv::ListMotions_Request(rosidl_runtime_cpp::MessageInitialization::ZERO);
}

}  // namespace play_motion2_msgs


namespace play_motion2_msgs
{

namespace srv
{

namespace builder
{

class Init_ListMotions_Response_motion_keys
{
public:
  Init_ListMotions_Response_motion_keys()
  : msg_(::rosidl_runtime_cpp::MessageInitialization::SKIP)
  {}
  ::play_motion2_msgs::srv::ListMotions_Response motion_keys(::play_motion2_msgs::srv::ListMotions_Response::_motion_keys_type arg)
  {
    msg_.motion_keys = std::move(arg);
    return std::move(msg_);
  }

private:
  ::play_motion2_msgs::srv::ListMotions_Response msg_;
};

}  // namespace builder

}  // namespace srv

template<typename MessageType>
auto build();

template<>
inline
auto build<::play_motion2_msgs::srv::ListMotions_Response>()
{
  return play_motion2_msgs::srv::builder::Init_ListMotions_Response_motion_keys();
}

}  // namespace play_motion2_msgs

#endif  // PLAY_MOTION2_MSGS__SRV__DETAIL__LIST_MOTIONS__BUILDER_HPP_
