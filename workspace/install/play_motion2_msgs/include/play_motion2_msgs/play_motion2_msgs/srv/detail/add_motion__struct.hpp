// generated from rosidl_generator_cpp/resource/idl__struct.hpp.em
// with input from play_motion2_msgs:srv/AddMotion.idl
// generated code does not contain a copyright notice

#ifndef PLAY_MOTION2_MSGS__SRV__DETAIL__ADD_MOTION__STRUCT_HPP_
#define PLAY_MOTION2_MSGS__SRV__DETAIL__ADD_MOTION__STRUCT_HPP_

#include <algorithm>
#include <array>
#include <cstdint>
#include <memory>
#include <string>
#include <vector>

#include "rosidl_runtime_cpp/bounded_vector.hpp"
#include "rosidl_runtime_cpp/message_initialization.hpp"


// Include directives for member types
// Member 'motion'
#include "play_motion2_msgs/msg/detail/motion__struct.hpp"

#ifndef _WIN32
# define DEPRECATED__play_motion2_msgs__srv__AddMotion_Request __attribute__((deprecated))
#else
# define DEPRECATED__play_motion2_msgs__srv__AddMotion_Request __declspec(deprecated)
#endif

namespace play_motion2_msgs
{

namespace srv
{

// message struct
template<class ContainerAllocator>
struct AddMotion_Request_
{
  using Type = AddMotion_Request_<ContainerAllocator>;

  explicit AddMotion_Request_(rosidl_runtime_cpp::MessageInitialization _init = rosidl_runtime_cpp::MessageInitialization::ALL)
  : motion(_init)
  {
    if (rosidl_runtime_cpp::MessageInitialization::ALL == _init ||
      rosidl_runtime_cpp::MessageInitialization::ZERO == _init)
    {
      this->overwrite = false;
    }
  }

  explicit AddMotion_Request_(const ContainerAllocator & _alloc, rosidl_runtime_cpp::MessageInitialization _init = rosidl_runtime_cpp::MessageInitialization::ALL)
  : motion(_alloc, _init)
  {
    if (rosidl_runtime_cpp::MessageInitialization::ALL == _init ||
      rosidl_runtime_cpp::MessageInitialization::ZERO == _init)
    {
      this->overwrite = false;
    }
  }

  // field types and members
  using _motion_type =
    play_motion2_msgs::msg::Motion_<ContainerAllocator>;
  _motion_type motion;
  using _overwrite_type =
    bool;
  _overwrite_type overwrite;

  // setters for named parameter idiom
  Type & set__motion(
    const play_motion2_msgs::msg::Motion_<ContainerAllocator> & _arg)
  {
    this->motion = _arg;
    return *this;
  }
  Type & set__overwrite(
    const bool & _arg)
  {
    this->overwrite = _arg;
    return *this;
  }

  // constant declarations

  // pointer types
  using RawPtr =
    play_motion2_msgs::srv::AddMotion_Request_<ContainerAllocator> *;
  using ConstRawPtr =
    const play_motion2_msgs::srv::AddMotion_Request_<ContainerAllocator> *;
  using SharedPtr =
    std::shared_ptr<play_motion2_msgs::srv::AddMotion_Request_<ContainerAllocator>>;
  using ConstSharedPtr =
    std::shared_ptr<play_motion2_msgs::srv::AddMotion_Request_<ContainerAllocator> const>;

  template<typename Deleter = std::default_delete<
      play_motion2_msgs::srv::AddMotion_Request_<ContainerAllocator>>>
  using UniquePtrWithDeleter =
    std::unique_ptr<play_motion2_msgs::srv::AddMotion_Request_<ContainerAllocator>, Deleter>;

  using UniquePtr = UniquePtrWithDeleter<>;

  template<typename Deleter = std::default_delete<
      play_motion2_msgs::srv::AddMotion_Request_<ContainerAllocator>>>
  using ConstUniquePtrWithDeleter =
    std::unique_ptr<play_motion2_msgs::srv::AddMotion_Request_<ContainerAllocator> const, Deleter>;
  using ConstUniquePtr = ConstUniquePtrWithDeleter<>;

  using WeakPtr =
    std::weak_ptr<play_motion2_msgs::srv::AddMotion_Request_<ContainerAllocator>>;
  using ConstWeakPtr =
    std::weak_ptr<play_motion2_msgs::srv::AddMotion_Request_<ContainerAllocator> const>;

  // pointer types similar to ROS 1, use SharedPtr / ConstSharedPtr instead
  // NOTE: Can't use 'using' here because GNU C++ can't parse attributes properly
  typedef DEPRECATED__play_motion2_msgs__srv__AddMotion_Request
    std::shared_ptr<play_motion2_msgs::srv::AddMotion_Request_<ContainerAllocator>>
    Ptr;
  typedef DEPRECATED__play_motion2_msgs__srv__AddMotion_Request
    std::shared_ptr<play_motion2_msgs::srv::AddMotion_Request_<ContainerAllocator> const>
    ConstPtr;

  // comparison operators
  bool operator==(const AddMotion_Request_ & other) const
  {
    if (this->motion != other.motion) {
      return false;
    }
    if (this->overwrite != other.overwrite) {
      return false;
    }
    return true;
  }
  bool operator!=(const AddMotion_Request_ & other) const
  {
    return !this->operator==(other);
  }
};  // struct AddMotion_Request_

// alias to use template instance with default allocator
using AddMotion_Request =
  play_motion2_msgs::srv::AddMotion_Request_<std::allocator<void>>;

// constant definitions

}  // namespace srv

}  // namespace play_motion2_msgs


#ifndef _WIN32
# define DEPRECATED__play_motion2_msgs__srv__AddMotion_Response __attribute__((deprecated))
#else
# define DEPRECATED__play_motion2_msgs__srv__AddMotion_Response __declspec(deprecated)
#endif

namespace play_motion2_msgs
{

namespace srv
{

// message struct
template<class ContainerAllocator>
struct AddMotion_Response_
{
  using Type = AddMotion_Response_<ContainerAllocator>;

  explicit AddMotion_Response_(rosidl_runtime_cpp::MessageInitialization _init = rosidl_runtime_cpp::MessageInitialization::ALL)
  {
    if (rosidl_runtime_cpp::MessageInitialization::ALL == _init ||
      rosidl_runtime_cpp::MessageInitialization::ZERO == _init)
    {
      this->success = false;
    }
  }

  explicit AddMotion_Response_(const ContainerAllocator & _alloc, rosidl_runtime_cpp::MessageInitialization _init = rosidl_runtime_cpp::MessageInitialization::ALL)
  {
    (void)_alloc;
    if (rosidl_runtime_cpp::MessageInitialization::ALL == _init ||
      rosidl_runtime_cpp::MessageInitialization::ZERO == _init)
    {
      this->success = false;
    }
  }

  // field types and members
  using _success_type =
    bool;
  _success_type success;

  // setters for named parameter idiom
  Type & set__success(
    const bool & _arg)
  {
    this->success = _arg;
    return *this;
  }

  // constant declarations

  // pointer types
  using RawPtr =
    play_motion2_msgs::srv::AddMotion_Response_<ContainerAllocator> *;
  using ConstRawPtr =
    const play_motion2_msgs::srv::AddMotion_Response_<ContainerAllocator> *;
  using SharedPtr =
    std::shared_ptr<play_motion2_msgs::srv::AddMotion_Response_<ContainerAllocator>>;
  using ConstSharedPtr =
    std::shared_ptr<play_motion2_msgs::srv::AddMotion_Response_<ContainerAllocator> const>;

  template<typename Deleter = std::default_delete<
      play_motion2_msgs::srv::AddMotion_Response_<ContainerAllocator>>>
  using UniquePtrWithDeleter =
    std::unique_ptr<play_motion2_msgs::srv::AddMotion_Response_<ContainerAllocator>, Deleter>;

  using UniquePtr = UniquePtrWithDeleter<>;

  template<typename Deleter = std::default_delete<
      play_motion2_msgs::srv::AddMotion_Response_<ContainerAllocator>>>
  using ConstUniquePtrWithDeleter =
    std::unique_ptr<play_motion2_msgs::srv::AddMotion_Response_<ContainerAllocator> const, Deleter>;
  using ConstUniquePtr = ConstUniquePtrWithDeleter<>;

  using WeakPtr =
    std::weak_ptr<play_motion2_msgs::srv::AddMotion_Response_<ContainerAllocator>>;
  using ConstWeakPtr =
    std::weak_ptr<play_motion2_msgs::srv::AddMotion_Response_<ContainerAllocator> const>;

  // pointer types similar to ROS 1, use SharedPtr / ConstSharedPtr instead
  // NOTE: Can't use 'using' here because GNU C++ can't parse attributes properly
  typedef DEPRECATED__play_motion2_msgs__srv__AddMotion_Response
    std::shared_ptr<play_motion2_msgs::srv::AddMotion_Response_<ContainerAllocator>>
    Ptr;
  typedef DEPRECATED__play_motion2_msgs__srv__AddMotion_Response
    std::shared_ptr<play_motion2_msgs::srv::AddMotion_Response_<ContainerAllocator> const>
    ConstPtr;

  // comparison operators
  bool operator==(const AddMotion_Response_ & other) const
  {
    if (this->success != other.success) {
      return false;
    }
    return true;
  }
  bool operator!=(const AddMotion_Response_ & other) const
  {
    return !this->operator==(other);
  }
};  // struct AddMotion_Response_

// alias to use template instance with default allocator
using AddMotion_Response =
  play_motion2_msgs::srv::AddMotion_Response_<std::allocator<void>>;

// constant definitions

}  // namespace srv

}  // namespace play_motion2_msgs

namespace play_motion2_msgs
{

namespace srv
{

struct AddMotion
{
  using Request = play_motion2_msgs::srv::AddMotion_Request;
  using Response = play_motion2_msgs::srv::AddMotion_Response;
};

}  // namespace srv

}  // namespace play_motion2_msgs

#endif  // PLAY_MOTION2_MSGS__SRV__DETAIL__ADD_MOTION__STRUCT_HPP_
