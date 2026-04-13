// generated from rosidl_generator_cpp/resource/idl__struct.hpp.em
// with input from hospital_interfaces:srv/AnalyzeActivity.idl
// generated code does not contain a copyright notice

#ifndef HOSPITAL_INTERFACES__SRV__DETAIL__ANALYZE_ACTIVITY__STRUCT_HPP_
#define HOSPITAL_INTERFACES__SRV__DETAIL__ANALYZE_ACTIVITY__STRUCT_HPP_

#include <algorithm>
#include <array>
#include <cstdint>
#include <memory>
#include <string>
#include <vector>

#include "rosidl_runtime_cpp/bounded_vector.hpp"
#include "rosidl_runtime_cpp/message_initialization.hpp"


#ifndef _WIN32
# define DEPRECATED__hospital_interfaces__srv__AnalyzeActivity_Request __attribute__((deprecated))
#else
# define DEPRECATED__hospital_interfaces__srv__AnalyzeActivity_Request __declspec(deprecated)
#endif

namespace hospital_interfaces
{

namespace srv
{

// message struct
template<class ContainerAllocator>
struct AnalyzeActivity_Request_
{
  using Type = AnalyzeActivity_Request_<ContainerAllocator>;

  explicit AnalyzeActivity_Request_(rosidl_runtime_cpp::MessageInitialization _init = rosidl_runtime_cpp::MessageInitialization::ALL)
  {
    if (rosidl_runtime_cpp::MessageInitialization::ALL == _init ||
      rosidl_runtime_cpp::MessageInitialization::ZERO == _init)
    {
      this->image_path = "";
      this->zone_name = "";
      this->time = "";
      this->expected_activities = "";
      this->zone_type = "";
    }
  }

  explicit AnalyzeActivity_Request_(const ContainerAllocator & _alloc, rosidl_runtime_cpp::MessageInitialization _init = rosidl_runtime_cpp::MessageInitialization::ALL)
  : image_path(_alloc),
    zone_name(_alloc),
    time(_alloc),
    expected_activities(_alloc),
    zone_type(_alloc)
  {
    if (rosidl_runtime_cpp::MessageInitialization::ALL == _init ||
      rosidl_runtime_cpp::MessageInitialization::ZERO == _init)
    {
      this->image_path = "";
      this->zone_name = "";
      this->time = "";
      this->expected_activities = "";
      this->zone_type = "";
    }
  }

  // field types and members
  using _image_path_type =
    std::basic_string<char, std::char_traits<char>, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<char>>;
  _image_path_type image_path;
  using _zone_name_type =
    std::basic_string<char, std::char_traits<char>, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<char>>;
  _zone_name_type zone_name;
  using _time_type =
    std::basic_string<char, std::char_traits<char>, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<char>>;
  _time_type time;
  using _expected_activities_type =
    std::basic_string<char, std::char_traits<char>, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<char>>;
  _expected_activities_type expected_activities;
  using _zone_type_type =
    std::basic_string<char, std::char_traits<char>, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<char>>;
  _zone_type_type zone_type;

  // setters for named parameter idiom
  Type & set__image_path(
    const std::basic_string<char, std::char_traits<char>, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<char>> & _arg)
  {
    this->image_path = _arg;
    return *this;
  }
  Type & set__zone_name(
    const std::basic_string<char, std::char_traits<char>, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<char>> & _arg)
  {
    this->zone_name = _arg;
    return *this;
  }
  Type & set__time(
    const std::basic_string<char, std::char_traits<char>, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<char>> & _arg)
  {
    this->time = _arg;
    return *this;
  }
  Type & set__expected_activities(
    const std::basic_string<char, std::char_traits<char>, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<char>> & _arg)
  {
    this->expected_activities = _arg;
    return *this;
  }
  Type & set__zone_type(
    const std::basic_string<char, std::char_traits<char>, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<char>> & _arg)
  {
    this->zone_type = _arg;
    return *this;
  }

  // constant declarations

  // pointer types
  using RawPtr =
    hospital_interfaces::srv::AnalyzeActivity_Request_<ContainerAllocator> *;
  using ConstRawPtr =
    const hospital_interfaces::srv::AnalyzeActivity_Request_<ContainerAllocator> *;
  using SharedPtr =
    std::shared_ptr<hospital_interfaces::srv::AnalyzeActivity_Request_<ContainerAllocator>>;
  using ConstSharedPtr =
    std::shared_ptr<hospital_interfaces::srv::AnalyzeActivity_Request_<ContainerAllocator> const>;

  template<typename Deleter = std::default_delete<
      hospital_interfaces::srv::AnalyzeActivity_Request_<ContainerAllocator>>>
  using UniquePtrWithDeleter =
    std::unique_ptr<hospital_interfaces::srv::AnalyzeActivity_Request_<ContainerAllocator>, Deleter>;

  using UniquePtr = UniquePtrWithDeleter<>;

  template<typename Deleter = std::default_delete<
      hospital_interfaces::srv::AnalyzeActivity_Request_<ContainerAllocator>>>
  using ConstUniquePtrWithDeleter =
    std::unique_ptr<hospital_interfaces::srv::AnalyzeActivity_Request_<ContainerAllocator> const, Deleter>;
  using ConstUniquePtr = ConstUniquePtrWithDeleter<>;

  using WeakPtr =
    std::weak_ptr<hospital_interfaces::srv::AnalyzeActivity_Request_<ContainerAllocator>>;
  using ConstWeakPtr =
    std::weak_ptr<hospital_interfaces::srv::AnalyzeActivity_Request_<ContainerAllocator> const>;

  // pointer types similar to ROS 1, use SharedPtr / ConstSharedPtr instead
  // NOTE: Can't use 'using' here because GNU C++ can't parse attributes properly
  typedef DEPRECATED__hospital_interfaces__srv__AnalyzeActivity_Request
    std::shared_ptr<hospital_interfaces::srv::AnalyzeActivity_Request_<ContainerAllocator>>
    Ptr;
  typedef DEPRECATED__hospital_interfaces__srv__AnalyzeActivity_Request
    std::shared_ptr<hospital_interfaces::srv::AnalyzeActivity_Request_<ContainerAllocator> const>
    ConstPtr;

  // comparison operators
  bool operator==(const AnalyzeActivity_Request_ & other) const
  {
    if (this->image_path != other.image_path) {
      return false;
    }
    if (this->zone_name != other.zone_name) {
      return false;
    }
    if (this->time != other.time) {
      return false;
    }
    if (this->expected_activities != other.expected_activities) {
      return false;
    }
    if (this->zone_type != other.zone_type) {
      return false;
    }
    return true;
  }
  bool operator!=(const AnalyzeActivity_Request_ & other) const
  {
    return !this->operator==(other);
  }
};  // struct AnalyzeActivity_Request_

// alias to use template instance with default allocator
using AnalyzeActivity_Request =
  hospital_interfaces::srv::AnalyzeActivity_Request_<std::allocator<void>>;

// constant definitions

}  // namespace srv

}  // namespace hospital_interfaces


#ifndef _WIN32
# define DEPRECATED__hospital_interfaces__srv__AnalyzeActivity_Response __attribute__((deprecated))
#else
# define DEPRECATED__hospital_interfaces__srv__AnalyzeActivity_Response __declspec(deprecated)
#endif

namespace hospital_interfaces
{

namespace srv
{

// message struct
template<class ContainerAllocator>
struct AnalyzeActivity_Response_
{
  using Type = AnalyzeActivity_Response_<ContainerAllocator>;

  explicit AnalyzeActivity_Response_(rosidl_runtime_cpp::MessageInitialization _init = rosidl_runtime_cpp::MessageInitialization::ALL)
  {
    if (rosidl_runtime_cpp::MessageInitialization::ALL == _init ||
      rosidl_runtime_cpp::MessageInitialization::ZERO == _init)
    {
      this->report = "";
    }
  }

  explicit AnalyzeActivity_Response_(const ContainerAllocator & _alloc, rosidl_runtime_cpp::MessageInitialization _init = rosidl_runtime_cpp::MessageInitialization::ALL)
  : report(_alloc)
  {
    if (rosidl_runtime_cpp::MessageInitialization::ALL == _init ||
      rosidl_runtime_cpp::MessageInitialization::ZERO == _init)
    {
      this->report = "";
    }
  }

  // field types and members
  using _report_type =
    std::basic_string<char, std::char_traits<char>, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<char>>;
  _report_type report;

  // setters for named parameter idiom
  Type & set__report(
    const std::basic_string<char, std::char_traits<char>, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<char>> & _arg)
  {
    this->report = _arg;
    return *this;
  }

  // constant declarations

  // pointer types
  using RawPtr =
    hospital_interfaces::srv::AnalyzeActivity_Response_<ContainerAllocator> *;
  using ConstRawPtr =
    const hospital_interfaces::srv::AnalyzeActivity_Response_<ContainerAllocator> *;
  using SharedPtr =
    std::shared_ptr<hospital_interfaces::srv::AnalyzeActivity_Response_<ContainerAllocator>>;
  using ConstSharedPtr =
    std::shared_ptr<hospital_interfaces::srv::AnalyzeActivity_Response_<ContainerAllocator> const>;

  template<typename Deleter = std::default_delete<
      hospital_interfaces::srv::AnalyzeActivity_Response_<ContainerAllocator>>>
  using UniquePtrWithDeleter =
    std::unique_ptr<hospital_interfaces::srv::AnalyzeActivity_Response_<ContainerAllocator>, Deleter>;

  using UniquePtr = UniquePtrWithDeleter<>;

  template<typename Deleter = std::default_delete<
      hospital_interfaces::srv::AnalyzeActivity_Response_<ContainerAllocator>>>
  using ConstUniquePtrWithDeleter =
    std::unique_ptr<hospital_interfaces::srv::AnalyzeActivity_Response_<ContainerAllocator> const, Deleter>;
  using ConstUniquePtr = ConstUniquePtrWithDeleter<>;

  using WeakPtr =
    std::weak_ptr<hospital_interfaces::srv::AnalyzeActivity_Response_<ContainerAllocator>>;
  using ConstWeakPtr =
    std::weak_ptr<hospital_interfaces::srv::AnalyzeActivity_Response_<ContainerAllocator> const>;

  // pointer types similar to ROS 1, use SharedPtr / ConstSharedPtr instead
  // NOTE: Can't use 'using' here because GNU C++ can't parse attributes properly
  typedef DEPRECATED__hospital_interfaces__srv__AnalyzeActivity_Response
    std::shared_ptr<hospital_interfaces::srv::AnalyzeActivity_Response_<ContainerAllocator>>
    Ptr;
  typedef DEPRECATED__hospital_interfaces__srv__AnalyzeActivity_Response
    std::shared_ptr<hospital_interfaces::srv::AnalyzeActivity_Response_<ContainerAllocator> const>
    ConstPtr;

  // comparison operators
  bool operator==(const AnalyzeActivity_Response_ & other) const
  {
    if (this->report != other.report) {
      return false;
    }
    return true;
  }
  bool operator!=(const AnalyzeActivity_Response_ & other) const
  {
    return !this->operator==(other);
  }
};  // struct AnalyzeActivity_Response_

// alias to use template instance with default allocator
using AnalyzeActivity_Response =
  hospital_interfaces::srv::AnalyzeActivity_Response_<std::allocator<void>>;

// constant definitions

}  // namespace srv

}  // namespace hospital_interfaces

namespace hospital_interfaces
{

namespace srv
{

struct AnalyzeActivity
{
  using Request = hospital_interfaces::srv::AnalyzeActivity_Request;
  using Response = hospital_interfaces::srv::AnalyzeActivity_Response;
};

}  // namespace srv

}  // namespace hospital_interfaces

#endif  // HOSPITAL_INTERFACES__SRV__DETAIL__ANALYZE_ACTIVITY__STRUCT_HPP_
