// generated from rosidl_generator_cpp/resource/idl__struct.hpp.em
// with input from play_motion2_msgs:srv/IsJointListReady.idl
// generated code does not contain a copyright notice

#ifndef PLAY_MOTION2_MSGS__SRV__DETAIL__IS_JOINT_LIST_READY__STRUCT_HPP_
#define PLAY_MOTION2_MSGS__SRV__DETAIL__IS_JOINT_LIST_READY__STRUCT_HPP_

#include <algorithm>
#include <array>
#include <cstdint>
#include <memory>
#include <string>
#include <vector>

#include "rosidl_runtime_cpp/bounded_vector.hpp"
#include "rosidl_runtime_cpp/message_initialization.hpp"


#ifndef _WIN32
# define DEPRECATED__play_motion2_msgs__srv__IsJointListReady_Request __attribute__((deprecated))
#else
# define DEPRECATED__play_motion2_msgs__srv__IsJointListReady_Request __declspec(deprecated)
#endif

namespace play_motion2_msgs
{

namespace srv
{

// message struct
template<class ContainerAllocator>
struct IsJointListReady_Request_
{
  using Type = IsJointListReady_Request_<ContainerAllocator>;

  explicit IsJointListReady_Request_(rosidl_runtime_cpp::MessageInitialization _init = rosidl_runtime_cpp::MessageInitialization::ALL)
  {
    (void)_init;
  }

  explicit IsJointListReady_Request_(const ContainerAllocator & _alloc, rosidl_runtime_cpp::MessageInitialization _init = rosidl_runtime_cpp::MessageInitialization::ALL)
  {
    (void)_init;
    (void)_alloc;
  }

  // field types and members
  using _joints_type =
    std::vector<std::basic_string<char, std::char_traits<char>, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<char>>, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<std::basic_string<char, std::char_traits<char>, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<char>>>>;
  _joints_type joints;

  // setters for named parameter idiom
  Type & set__joints(
    const std::vector<std::basic_string<char, std::char_traits<char>, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<char>>, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<std::basic_string<char, std::char_traits<char>, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<char>>>> & _arg)
  {
    this->joints = _arg;
    return *this;
  }

  // constant declarations

  // pointer types
  using RawPtr =
    play_motion2_msgs::srv::IsJointListReady_Request_<ContainerAllocator> *;
  using ConstRawPtr =
    const play_motion2_msgs::srv::IsJointListReady_Request_<ContainerAllocator> *;
  using SharedPtr =
    std::shared_ptr<play_motion2_msgs::srv::IsJointListReady_Request_<ContainerAllocator>>;
  using ConstSharedPtr =
    std::shared_ptr<play_motion2_msgs::srv::IsJointListReady_Request_<ContainerAllocator> const>;

  template<typename Deleter = std::default_delete<
      play_motion2_msgs::srv::IsJointListReady_Request_<ContainerAllocator>>>
  using UniquePtrWithDeleter =
    std::unique_ptr<play_motion2_msgs::srv::IsJointListReady_Request_<ContainerAllocator>, Deleter>;

  using UniquePtr = UniquePtrWithDeleter<>;

  template<typename Deleter = std::default_delete<
      play_motion2_msgs::srv::IsJointListReady_Request_<ContainerAllocator>>>
  using ConstUniquePtrWithDeleter =
    std::unique_ptr<play_motion2_msgs::srv::IsJointListReady_Request_<ContainerAllocator> const, Deleter>;
  using ConstUniquePtr = ConstUniquePtrWithDeleter<>;

  using WeakPtr =
    std::weak_ptr<play_motion2_msgs::srv::IsJointListReady_Request_<ContainerAllocator>>;
  using ConstWeakPtr =
    std::weak_ptr<play_motion2_msgs::srv::IsJointListReady_Request_<ContainerAllocator> const>;

  // pointer types similar to ROS 1, use SharedPtr / ConstSharedPtr instead
  // NOTE: Can't use 'using' here because GNU C++ can't parse attributes properly
  typedef DEPRECATED__play_motion2_msgs__srv__IsJointListReady_Request
    std::shared_ptr<play_motion2_msgs::srv::IsJointListReady_Request_<ContainerAllocator>>
    Ptr;
  typedef DEPRECATED__play_motion2_msgs__srv__IsJointListReady_Request
    std::shared_ptr<play_motion2_msgs::srv::IsJointListReady_Request_<ContainerAllocator> const>
    ConstPtr;

  // comparison operators
  bool operator==(const IsJointListReady_Request_ & other) const
  {
    if (this->joints != other.joints) {
      return false;
    }
    return true;
  }
  bool operator!=(const IsJointListReady_Request_ & other) const
  {
    return !this->operator==(other);
  }
};  // struct IsJointListReady_Request_

// alias to use template instance with default allocator
using IsJointListReady_Request =
  play_motion2_msgs::srv::IsJointListReady_Request_<std::allocator<void>>;

// constant definitions

}  // namespace srv

}  // namespace play_motion2_msgs


#ifndef _WIN32
# define DEPRECATED__play_motion2_msgs__srv__IsJointListReady_Response __attribute__((deprecated))
#else
# define DEPRECATED__play_motion2_msgs__srv__IsJointListReady_Response __declspec(deprecated)
#endif

namespace play_motion2_msgs
{

namespace srv
{

// message struct
template<class ContainerAllocator>
struct IsJointListReady_Response_
{
  using Type = IsJointListReady_Response_<ContainerAllocator>;

  explicit IsJointListReady_Response_(rosidl_runtime_cpp::MessageInitialization _init = rosidl_runtime_cpp::MessageInitialization::ALL)
  {
    if (rosidl_runtime_cpp::MessageInitialization::ALL == _init ||
      rosidl_runtime_cpp::MessageInitialization::ZERO == _init)
    {
      this->is_ready = false;
    }
  }

  explicit IsJointListReady_Response_(const ContainerAllocator & _alloc, rosidl_runtime_cpp::MessageInitialization _init = rosidl_runtime_cpp::MessageInitialization::ALL)
  {
    (void)_alloc;
    if (rosidl_runtime_cpp::MessageInitialization::ALL == _init ||
      rosidl_runtime_cpp::MessageInitialization::ZERO == _init)
    {
      this->is_ready = false;
    }
  }

  // field types and members
  using _is_ready_type =
    bool;
  _is_ready_type is_ready;

  // setters for named parameter idiom
  Type & set__is_ready(
    const bool & _arg)
  {
    this->is_ready = _arg;
    return *this;
  }

  // constant declarations

  // pointer types
  using RawPtr =
    play_motion2_msgs::srv::IsJointListReady_Response_<ContainerAllocator> *;
  using ConstRawPtr =
    const play_motion2_msgs::srv::IsJointListReady_Response_<ContainerAllocator> *;
  using SharedPtr =
    std::shared_ptr<play_motion2_msgs::srv::IsJointListReady_Response_<ContainerAllocator>>;
  using ConstSharedPtr =
    std::shared_ptr<play_motion2_msgs::srv::IsJointListReady_Response_<ContainerAllocator> const>;

  template<typename Deleter = std::default_delete<
      play_motion2_msgs::srv::IsJointListReady_Response_<ContainerAllocator>>>
  using UniquePtrWithDeleter =
    std::unique_ptr<play_motion2_msgs::srv::IsJointListReady_Response_<ContainerAllocator>, Deleter>;

  using UniquePtr = UniquePtrWithDeleter<>;

  template<typename Deleter = std::default_delete<
      play_motion2_msgs::srv::IsJointListReady_Response_<ContainerAllocator>>>
  using ConstUniquePtrWithDeleter =
    std::unique_ptr<play_motion2_msgs::srv::IsJointListReady_Response_<ContainerAllocator> const, Deleter>;
  using ConstUniquePtr = ConstUniquePtrWithDeleter<>;

  using WeakPtr =
    std::weak_ptr<play_motion2_msgs::srv::IsJointListReady_Response_<ContainerAllocator>>;
  using ConstWeakPtr =
    std::weak_ptr<play_motion2_msgs::srv::IsJointListReady_Response_<ContainerAllocator> const>;

  // pointer types similar to ROS 1, use SharedPtr / ConstSharedPtr instead
  // NOTE: Can't use 'using' here because GNU C++ can't parse attributes properly
  typedef DEPRECATED__play_motion2_msgs__srv__IsJointListReady_Response
    std::shared_ptr<play_motion2_msgs::srv::IsJointListReady_Response_<ContainerAllocator>>
    Ptr;
  typedef DEPRECATED__play_motion2_msgs__srv__IsJointListReady_Response
    std::shared_ptr<play_motion2_msgs::srv::IsJointListReady_Response_<ContainerAllocator> const>
    ConstPtr;

  // comparison operators
  bool operator==(const IsJointListReady_Response_ & other) const
  {
    if (this->is_ready != other.is_ready) {
      return false;
    }
    return true;
  }
  bool operator!=(const IsJointListReady_Response_ & other) const
  {
    return !this->operator==(other);
  }
};  // struct IsJointListReady_Response_

// alias to use template instance with default allocator
using IsJointListReady_Response =
  play_motion2_msgs::srv::IsJointListReady_Response_<std::allocator<void>>;

// constant definitions

}  // namespace srv

}  // namespace play_motion2_msgs

namespace play_motion2_msgs
{

namespace srv
{

struct IsJointListReady
{
  using Request = play_motion2_msgs::srv::IsJointListReady_Request;
  using Response = play_motion2_msgs::srv::IsJointListReady_Response;
};

}  // namespace srv

}  // namespace play_motion2_msgs

#endif  // PLAY_MOTION2_MSGS__SRV__DETAIL__IS_JOINT_LIST_READY__STRUCT_HPP_
