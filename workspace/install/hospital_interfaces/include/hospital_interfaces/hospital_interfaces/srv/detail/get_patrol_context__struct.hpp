// generated from rosidl_generator_cpp/resource/idl__struct.hpp.em
// with input from hospital_interfaces:srv/GetPatrolContext.idl
// generated code does not contain a copyright notice

#ifndef HOSPITAL_INTERFACES__SRV__DETAIL__GET_PATROL_CONTEXT__STRUCT_HPP_
#define HOSPITAL_INTERFACES__SRV__DETAIL__GET_PATROL_CONTEXT__STRUCT_HPP_

#include <algorithm>
#include <array>
#include <cstdint>
#include <memory>
#include <string>
#include <vector>

#include "rosidl_runtime_cpp/bounded_vector.hpp"
#include "rosidl_runtime_cpp/message_initialization.hpp"


#ifndef _WIN32
# define DEPRECATED__hospital_interfaces__srv__GetPatrolContext_Request __attribute__((deprecated))
#else
# define DEPRECATED__hospital_interfaces__srv__GetPatrolContext_Request __declspec(deprecated)
#endif

namespace hospital_interfaces
{

namespace srv
{

// message struct
template<class ContainerAllocator>
struct GetPatrolContext_Request_
{
  using Type = GetPatrolContext_Request_<ContainerAllocator>;

  explicit GetPatrolContext_Request_(rosidl_runtime_cpp::MessageInitialization _init = rosidl_runtime_cpp::MessageInitialization::ALL)
  {
    if (rosidl_runtime_cpp::MessageInitialization::ALL == _init ||
      rosidl_runtime_cpp::MessageInitialization::ZERO == _init)
    {
      this->structure_needs_at_least_one_member = 0;
    }
  }

  explicit GetPatrolContext_Request_(const ContainerAllocator & _alloc, rosidl_runtime_cpp::MessageInitialization _init = rosidl_runtime_cpp::MessageInitialization::ALL)
  {
    (void)_alloc;
    if (rosidl_runtime_cpp::MessageInitialization::ALL == _init ||
      rosidl_runtime_cpp::MessageInitialization::ZERO == _init)
    {
      this->structure_needs_at_least_one_member = 0;
    }
  }

  // field types and members
  using _structure_needs_at_least_one_member_type =
    uint8_t;
  _structure_needs_at_least_one_member_type structure_needs_at_least_one_member;


  // constant declarations

  // pointer types
  using RawPtr =
    hospital_interfaces::srv::GetPatrolContext_Request_<ContainerAllocator> *;
  using ConstRawPtr =
    const hospital_interfaces::srv::GetPatrolContext_Request_<ContainerAllocator> *;
  using SharedPtr =
    std::shared_ptr<hospital_interfaces::srv::GetPatrolContext_Request_<ContainerAllocator>>;
  using ConstSharedPtr =
    std::shared_ptr<hospital_interfaces::srv::GetPatrolContext_Request_<ContainerAllocator> const>;

  template<typename Deleter = std::default_delete<
      hospital_interfaces::srv::GetPatrolContext_Request_<ContainerAllocator>>>
  using UniquePtrWithDeleter =
    std::unique_ptr<hospital_interfaces::srv::GetPatrolContext_Request_<ContainerAllocator>, Deleter>;

  using UniquePtr = UniquePtrWithDeleter<>;

  template<typename Deleter = std::default_delete<
      hospital_interfaces::srv::GetPatrolContext_Request_<ContainerAllocator>>>
  using ConstUniquePtrWithDeleter =
    std::unique_ptr<hospital_interfaces::srv::GetPatrolContext_Request_<ContainerAllocator> const, Deleter>;
  using ConstUniquePtr = ConstUniquePtrWithDeleter<>;

  using WeakPtr =
    std::weak_ptr<hospital_interfaces::srv::GetPatrolContext_Request_<ContainerAllocator>>;
  using ConstWeakPtr =
    std::weak_ptr<hospital_interfaces::srv::GetPatrolContext_Request_<ContainerAllocator> const>;

  // pointer types similar to ROS 1, use SharedPtr / ConstSharedPtr instead
  // NOTE: Can't use 'using' here because GNU C++ can't parse attributes properly
  typedef DEPRECATED__hospital_interfaces__srv__GetPatrolContext_Request
    std::shared_ptr<hospital_interfaces::srv::GetPatrolContext_Request_<ContainerAllocator>>
    Ptr;
  typedef DEPRECATED__hospital_interfaces__srv__GetPatrolContext_Request
    std::shared_ptr<hospital_interfaces::srv::GetPatrolContext_Request_<ContainerAllocator> const>
    ConstPtr;

  // comparison operators
  bool operator==(const GetPatrolContext_Request_ & other) const
  {
    if (this->structure_needs_at_least_one_member != other.structure_needs_at_least_one_member) {
      return false;
    }
    return true;
  }
  bool operator!=(const GetPatrolContext_Request_ & other) const
  {
    return !this->operator==(other);
  }
};  // struct GetPatrolContext_Request_

// alias to use template instance with default allocator
using GetPatrolContext_Request =
  hospital_interfaces::srv::GetPatrolContext_Request_<std::allocator<void>>;

// constant definitions

}  // namespace srv

}  // namespace hospital_interfaces


#ifndef _WIN32
# define DEPRECATED__hospital_interfaces__srv__GetPatrolContext_Response __attribute__((deprecated))
#else
# define DEPRECATED__hospital_interfaces__srv__GetPatrolContext_Response __declspec(deprecated)
#endif

namespace hospital_interfaces
{

namespace srv
{

// message struct
template<class ContainerAllocator>
struct GetPatrolContext_Response_
{
  using Type = GetPatrolContext_Response_<ContainerAllocator>;

  explicit GetPatrolContext_Response_(rosidl_runtime_cpp::MessageInitialization _init = rosidl_runtime_cpp::MessageInitialization::ALL)
  {
    if (rosidl_runtime_cpp::MessageInitialization::ALL == _init ||
      rosidl_runtime_cpp::MessageInitialization::ZERO == _init)
    {
      this->success = false;
      this->global_context = "";
      this->final_summary = "";
    }
  }

  explicit GetPatrolContext_Response_(const ContainerAllocator & _alloc, rosidl_runtime_cpp::MessageInitialization _init = rosidl_runtime_cpp::MessageInitialization::ALL)
  : global_context(_alloc),
    final_summary(_alloc)
  {
    if (rosidl_runtime_cpp::MessageInitialization::ALL == _init ||
      rosidl_runtime_cpp::MessageInitialization::ZERO == _init)
    {
      this->success = false;
      this->global_context = "";
      this->final_summary = "";
    }
  }

  // field types and members
  using _success_type =
    bool;
  _success_type success;
  using _global_context_type =
    std::basic_string<char, std::char_traits<char>, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<char>>;
  _global_context_type global_context;
  using _final_summary_type =
    std::basic_string<char, std::char_traits<char>, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<char>>;
  _final_summary_type final_summary;

  // setters for named parameter idiom
  Type & set__success(
    const bool & _arg)
  {
    this->success = _arg;
    return *this;
  }
  Type & set__global_context(
    const std::basic_string<char, std::char_traits<char>, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<char>> & _arg)
  {
    this->global_context = _arg;
    return *this;
  }
  Type & set__final_summary(
    const std::basic_string<char, std::char_traits<char>, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<char>> & _arg)
  {
    this->final_summary = _arg;
    return *this;
  }

  // constant declarations

  // pointer types
  using RawPtr =
    hospital_interfaces::srv::GetPatrolContext_Response_<ContainerAllocator> *;
  using ConstRawPtr =
    const hospital_interfaces::srv::GetPatrolContext_Response_<ContainerAllocator> *;
  using SharedPtr =
    std::shared_ptr<hospital_interfaces::srv::GetPatrolContext_Response_<ContainerAllocator>>;
  using ConstSharedPtr =
    std::shared_ptr<hospital_interfaces::srv::GetPatrolContext_Response_<ContainerAllocator> const>;

  template<typename Deleter = std::default_delete<
      hospital_interfaces::srv::GetPatrolContext_Response_<ContainerAllocator>>>
  using UniquePtrWithDeleter =
    std::unique_ptr<hospital_interfaces::srv::GetPatrolContext_Response_<ContainerAllocator>, Deleter>;

  using UniquePtr = UniquePtrWithDeleter<>;

  template<typename Deleter = std::default_delete<
      hospital_interfaces::srv::GetPatrolContext_Response_<ContainerAllocator>>>
  using ConstUniquePtrWithDeleter =
    std::unique_ptr<hospital_interfaces::srv::GetPatrolContext_Response_<ContainerAllocator> const, Deleter>;
  using ConstUniquePtr = ConstUniquePtrWithDeleter<>;

  using WeakPtr =
    std::weak_ptr<hospital_interfaces::srv::GetPatrolContext_Response_<ContainerAllocator>>;
  using ConstWeakPtr =
    std::weak_ptr<hospital_interfaces::srv::GetPatrolContext_Response_<ContainerAllocator> const>;

  // pointer types similar to ROS 1, use SharedPtr / ConstSharedPtr instead
  // NOTE: Can't use 'using' here because GNU C++ can't parse attributes properly
  typedef DEPRECATED__hospital_interfaces__srv__GetPatrolContext_Response
    std::shared_ptr<hospital_interfaces::srv::GetPatrolContext_Response_<ContainerAllocator>>
    Ptr;
  typedef DEPRECATED__hospital_interfaces__srv__GetPatrolContext_Response
    std::shared_ptr<hospital_interfaces::srv::GetPatrolContext_Response_<ContainerAllocator> const>
    ConstPtr;

  // comparison operators
  bool operator==(const GetPatrolContext_Response_ & other) const
  {
    if (this->success != other.success) {
      return false;
    }
    if (this->global_context != other.global_context) {
      return false;
    }
    if (this->final_summary != other.final_summary) {
      return false;
    }
    return true;
  }
  bool operator!=(const GetPatrolContext_Response_ & other) const
  {
    return !this->operator==(other);
  }
};  // struct GetPatrolContext_Response_

// alias to use template instance with default allocator
using GetPatrolContext_Response =
  hospital_interfaces::srv::GetPatrolContext_Response_<std::allocator<void>>;

// constant definitions

}  // namespace srv

}  // namespace hospital_interfaces

namespace hospital_interfaces
{

namespace srv
{

struct GetPatrolContext
{
  using Request = hospital_interfaces::srv::GetPatrolContext_Request;
  using Response = hospital_interfaces::srv::GetPatrolContext_Response;
};

}  // namespace srv

}  // namespace hospital_interfaces

#endif  // HOSPITAL_INTERFACES__SRV__DETAIL__GET_PATROL_CONTEXT__STRUCT_HPP_
