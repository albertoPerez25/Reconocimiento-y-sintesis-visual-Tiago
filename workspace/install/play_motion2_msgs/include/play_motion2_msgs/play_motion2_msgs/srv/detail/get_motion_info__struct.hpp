// generated from rosidl_generator_cpp/resource/idl__struct.hpp.em
// with input from play_motion2_msgs:srv/GetMotionInfo.idl
// generated code does not contain a copyright notice

#ifndef PLAY_MOTION2_MSGS__SRV__DETAIL__GET_MOTION_INFO__STRUCT_HPP_
#define PLAY_MOTION2_MSGS__SRV__DETAIL__GET_MOTION_INFO__STRUCT_HPP_

#include <algorithm>
#include <array>
#include <cstdint>
#include <memory>
#include <string>
#include <vector>

#include "rosidl_runtime_cpp/bounded_vector.hpp"
#include "rosidl_runtime_cpp/message_initialization.hpp"


#ifndef _WIN32
# define DEPRECATED__play_motion2_msgs__srv__GetMotionInfo_Request __attribute__((deprecated))
#else
# define DEPRECATED__play_motion2_msgs__srv__GetMotionInfo_Request __declspec(deprecated)
#endif

namespace play_motion2_msgs
{

namespace srv
{

// message struct
template<class ContainerAllocator>
struct GetMotionInfo_Request_
{
  using Type = GetMotionInfo_Request_<ContainerAllocator>;

  explicit GetMotionInfo_Request_(rosidl_runtime_cpp::MessageInitialization _init = rosidl_runtime_cpp::MessageInitialization::ALL)
  {
    if (rosidl_runtime_cpp::MessageInitialization::ALL == _init ||
      rosidl_runtime_cpp::MessageInitialization::ZERO == _init)
    {
      this->motion_key = "";
    }
  }

  explicit GetMotionInfo_Request_(const ContainerAllocator & _alloc, rosidl_runtime_cpp::MessageInitialization _init = rosidl_runtime_cpp::MessageInitialization::ALL)
  : motion_key(_alloc)
  {
    if (rosidl_runtime_cpp::MessageInitialization::ALL == _init ||
      rosidl_runtime_cpp::MessageInitialization::ZERO == _init)
    {
      this->motion_key = "";
    }
  }

  // field types and members
  using _motion_key_type =
    std::basic_string<char, std::char_traits<char>, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<char>>;
  _motion_key_type motion_key;

  // setters for named parameter idiom
  Type & set__motion_key(
    const std::basic_string<char, std::char_traits<char>, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<char>> & _arg)
  {
    this->motion_key = _arg;
    return *this;
  }

  // constant declarations

  // pointer types
  using RawPtr =
    play_motion2_msgs::srv::GetMotionInfo_Request_<ContainerAllocator> *;
  using ConstRawPtr =
    const play_motion2_msgs::srv::GetMotionInfo_Request_<ContainerAllocator> *;
  using SharedPtr =
    std::shared_ptr<play_motion2_msgs::srv::GetMotionInfo_Request_<ContainerAllocator>>;
  using ConstSharedPtr =
    std::shared_ptr<play_motion2_msgs::srv::GetMotionInfo_Request_<ContainerAllocator> const>;

  template<typename Deleter = std::default_delete<
      play_motion2_msgs::srv::GetMotionInfo_Request_<ContainerAllocator>>>
  using UniquePtrWithDeleter =
    std::unique_ptr<play_motion2_msgs::srv::GetMotionInfo_Request_<ContainerAllocator>, Deleter>;

  using UniquePtr = UniquePtrWithDeleter<>;

  template<typename Deleter = std::default_delete<
      play_motion2_msgs::srv::GetMotionInfo_Request_<ContainerAllocator>>>
  using ConstUniquePtrWithDeleter =
    std::unique_ptr<play_motion2_msgs::srv::GetMotionInfo_Request_<ContainerAllocator> const, Deleter>;
  using ConstUniquePtr = ConstUniquePtrWithDeleter<>;

  using WeakPtr =
    std::weak_ptr<play_motion2_msgs::srv::GetMotionInfo_Request_<ContainerAllocator>>;
  using ConstWeakPtr =
    std::weak_ptr<play_motion2_msgs::srv::GetMotionInfo_Request_<ContainerAllocator> const>;

  // pointer types similar to ROS 1, use SharedPtr / ConstSharedPtr instead
  // NOTE: Can't use 'using' here because GNU C++ can't parse attributes properly
  typedef DEPRECATED__play_motion2_msgs__srv__GetMotionInfo_Request
    std::shared_ptr<play_motion2_msgs::srv::GetMotionInfo_Request_<ContainerAllocator>>
    Ptr;
  typedef DEPRECATED__play_motion2_msgs__srv__GetMotionInfo_Request
    std::shared_ptr<play_motion2_msgs::srv::GetMotionInfo_Request_<ContainerAllocator> const>
    ConstPtr;

  // comparison operators
  bool operator==(const GetMotionInfo_Request_ & other) const
  {
    if (this->motion_key != other.motion_key) {
      return false;
    }
    return true;
  }
  bool operator!=(const GetMotionInfo_Request_ & other) const
  {
    return !this->operator==(other);
  }
};  // struct GetMotionInfo_Request_

// alias to use template instance with default allocator
using GetMotionInfo_Request =
  play_motion2_msgs::srv::GetMotionInfo_Request_<std::allocator<void>>;

// constant definitions

}  // namespace srv

}  // namespace play_motion2_msgs


// Include directives for member types
// Member 'motion'
#include "play_motion2_msgs/msg/detail/motion__struct.hpp"

#ifndef _WIN32
# define DEPRECATED__play_motion2_msgs__srv__GetMotionInfo_Response __attribute__((deprecated))
#else
# define DEPRECATED__play_motion2_msgs__srv__GetMotionInfo_Response __declspec(deprecated)
#endif

namespace play_motion2_msgs
{

namespace srv
{

// message struct
template<class ContainerAllocator>
struct GetMotionInfo_Response_
{
  using Type = GetMotionInfo_Response_<ContainerAllocator>;

  explicit GetMotionInfo_Response_(rosidl_runtime_cpp::MessageInitialization _init = rosidl_runtime_cpp::MessageInitialization::ALL)
  : motion(_init)
  {
    (void)_init;
  }

  explicit GetMotionInfo_Response_(const ContainerAllocator & _alloc, rosidl_runtime_cpp::MessageInitialization _init = rosidl_runtime_cpp::MessageInitialization::ALL)
  : motion(_alloc, _init)
  {
    (void)_init;
  }

  // field types and members
  using _motion_type =
    play_motion2_msgs::msg::Motion_<ContainerAllocator>;
  _motion_type motion;

  // setters for named parameter idiom
  Type & set__motion(
    const play_motion2_msgs::msg::Motion_<ContainerAllocator> & _arg)
  {
    this->motion = _arg;
    return *this;
  }

  // constant declarations

  // pointer types
  using RawPtr =
    play_motion2_msgs::srv::GetMotionInfo_Response_<ContainerAllocator> *;
  using ConstRawPtr =
    const play_motion2_msgs::srv::GetMotionInfo_Response_<ContainerAllocator> *;
  using SharedPtr =
    std::shared_ptr<play_motion2_msgs::srv::GetMotionInfo_Response_<ContainerAllocator>>;
  using ConstSharedPtr =
    std::shared_ptr<play_motion2_msgs::srv::GetMotionInfo_Response_<ContainerAllocator> const>;

  template<typename Deleter = std::default_delete<
      play_motion2_msgs::srv::GetMotionInfo_Response_<ContainerAllocator>>>
  using UniquePtrWithDeleter =
    std::unique_ptr<play_motion2_msgs::srv::GetMotionInfo_Response_<ContainerAllocator>, Deleter>;

  using UniquePtr = UniquePtrWithDeleter<>;

  template<typename Deleter = std::default_delete<
      play_motion2_msgs::srv::GetMotionInfo_Response_<ContainerAllocator>>>
  using ConstUniquePtrWithDeleter =
    std::unique_ptr<play_motion2_msgs::srv::GetMotionInfo_Response_<ContainerAllocator> const, Deleter>;
  using ConstUniquePtr = ConstUniquePtrWithDeleter<>;

  using WeakPtr =
    std::weak_ptr<play_motion2_msgs::srv::GetMotionInfo_Response_<ContainerAllocator>>;
  using ConstWeakPtr =
    std::weak_ptr<play_motion2_msgs::srv::GetMotionInfo_Response_<ContainerAllocator> const>;

  // pointer types similar to ROS 1, use SharedPtr / ConstSharedPtr instead
  // NOTE: Can't use 'using' here because GNU C++ can't parse attributes properly
  typedef DEPRECATED__play_motion2_msgs__srv__GetMotionInfo_Response
    std::shared_ptr<play_motion2_msgs::srv::GetMotionInfo_Response_<ContainerAllocator>>
    Ptr;
  typedef DEPRECATED__play_motion2_msgs__srv__GetMotionInfo_Response
    std::shared_ptr<play_motion2_msgs::srv::GetMotionInfo_Response_<ContainerAllocator> const>
    ConstPtr;

  // comparison operators
  bool operator==(const GetMotionInfo_Response_ & other) const
  {
    if (this->motion != other.motion) {
      return false;
    }
    return true;
  }
  bool operator!=(const GetMotionInfo_Response_ & other) const
  {
    return !this->operator==(other);
  }
};  // struct GetMotionInfo_Response_

// alias to use template instance with default allocator
using GetMotionInfo_Response =
  play_motion2_msgs::srv::GetMotionInfo_Response_<std::allocator<void>>;

// constant definitions

}  // namespace srv

}  // namespace play_motion2_msgs

namespace play_motion2_msgs
{

namespace srv
{

struct GetMotionInfo
{
  using Request = play_motion2_msgs::srv::GetMotionInfo_Request;
  using Response = play_motion2_msgs::srv::GetMotionInfo_Response;
};

}  // namespace srv

}  // namespace play_motion2_msgs

#endif  // PLAY_MOTION2_MSGS__SRV__DETAIL__GET_MOTION_INFO__STRUCT_HPP_
