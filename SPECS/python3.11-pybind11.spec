%global __python3 /usr/bin/python3.11
%global python3_pkgversion 3.11

# While the headers are architecture independent, the package must be
# built separately on all architectures so that the tests are run
# properly. See also
# https://fedoraproject.org/wiki/Packaging:Guidelines#Packaging_Header_Only_Libraries
%global debug_package %{nil}

# Whether to run the tests, enabled by default
%bcond_without tests

%global modname pybind11

Name:    python%{python3_pkgversion}-pybind11
Version: 2.10.3
Release: 2%{?dist}
Summary: Seamless operability between C++11 and Python
License: BSD
URL:   https://github.com/pybind/pybind11
Source0: https://github.com/pybind/pybind11/archive/v%{version}/%{modname}-%{version}.tar.gz

# Patch out header path
Patch1:  pybind11-2.10.1-hpath.patch

BuildRequires: make

# Needed to build the python libraries
BuildRequires: python%{python3_pkgversion}-devel
BuildRequires: python%{python3_pkgversion}-rpm-macros
BuildRequires: python%{python3_pkgversion}-setuptools
# These are only needed for the checks
%if %{with tests}
BuildRequires: python%{python3_pkgversion}-pytest
BuildRequires: python%{python3_pkgversion}-numpy
BuildRequires: python%{python3_pkgversion}-scipy
%endif

BuildRequires: eigen3-devel
BuildRequires: gcc-c++
BuildRequires: cmake

Requires: %{name}-devel%{?_isa} = %{version}-%{release}

%global base_description \
pybind11 is a lightweight header-only library that exposes C++ types \
in Python and vice versa, mainly to create Python bindings of existing \
C++ code.

%description
%{base_description}

%package devel
Summary:  Development headers for pybind11

# This package does not have namespaced file locations, so if we build the
# pybind11-devel subpackage in any other stack as well, the files from these
# packages will conflict. The package name is namespaced so that customers can
# decide which to install, but the packages will conflict with each other.
Provides:   %{modname}-devel = %{version}-%{release}
Conflicts:  %{modname}-devel < %{version}-%{release} 

# https://fedoraproject.org/wiki/Packaging:Guidelines#Packaging_Header_Only_Libraries
Provides: %{modname}-static = %{version}-%{release}
Provides: %{name}-static = %{version}-%{release}
# For dir ownership
Requires: cmake

%description devel
%{base_description}

This package contains the development headers for pybind11.

%prep
%autosetup -p1 -n %{modname}-%{version}

%build
py=python3
mkdir $py
# When -DCMAKE_BUILD_TYPE is set to Release, the tests in %%check might segfault.
# However, we do not ship any binaries, and therefore Debug
# build type does not affect the results.
# https://bugzilla.redhat.com/show_bug.cgi?id=1921199
%if 0%{?rhel} < 9
cd $py
%cmake .. -DCMAKE_BUILD_TYPE=Debug -DPYTHON_EXECUTABLE=%{__python3} -DPYBIND11_INSTALL=TRUE -DUSE_PYTHON_INCLUDE_DIR=FALSE %{!?with_tests:-DPYBIND11_TEST=OFF}
%make_build
cd ..
%else
%cmake -B $py -DCMAKE_BUILD_TYPE=Debug -DPYTHON_EXECUTABLE=%{__python3} -DPYBIND11_INSTALL=TRUE -DUSE_PYTHON_INCLUDE_DIR=FALSE %{!?with_tests:-DPYBIND11_TEST=OFF}
%make_build -C $py
%endif

%py3_build

%if %{with tests}
%check
make -C python3 check %{?_smp_mflags}
%endif

%install
%make_install -C python3
# Force install to arch-ful directories instead.
PYBIND11_USE_CMAKE=true %py3_install "--install-purelib" "%{python3_sitearch}"

%files devel
%license LICENSE
%doc README.rst
%{_includedir}/pybind11/
%{_datadir}/cmake/pybind11/
%{_bindir}/pybind11-config
%{_datadir}/pkgconfig/%{modname}.pc

%files
%{python3_sitearch}/%{modname}/
%{python3_sitearch}/%{modname}-%{version}-py%{python3_version}.egg-info

%changelog
* Mon Feb 20 2023 Charalampos Stratakis <cstratak@redhat.com> - 2.10.3-2
- Enable tests

* Thu Dec 01 2022 Charalampos Stratakis <cstratak@redhat.com> - 2.10.3-1
- Initial package
- Fedora contributions by:
      Elliott Sales de Andrade <quantum.analyst@gmail.com>
      Jonathan <jonathan@knownhost.com>
      jonathanspw <jonathan@almalinux.org>
      Merlin Mathesius <mmathesi@redhat.com>
      Miro Hrončok <miro@hroncok.cz>
      Susi Lehtola <jussilehtola@fedoraproject.org>
      Tom Stellard <tstellar@redhat.com>
