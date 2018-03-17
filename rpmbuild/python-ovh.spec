%global pypi_name ovh

%global with_test 0

%if 0%{?rhel} && 0%{?rhel} <= 7
%bcond_with python3
%else
%bcond_without python3
%endif

# sitelib for noarch packages, sitearch for others (remove the unneeded one)
%{!?python_sitelib: %global python_sitelib %(%{__python} -c "from distutils.sysconfig import get_python_lib; print(get_python_lib())")}
%{!?python_sitearch: %global python_sitearch %(%{__python} -c "from distutils.sysconfig import get_python_lib; print(get_python_lib(1))")}

Name:		python-%{pypi_name}
Version:	0.4.8
Release:	1%{?dist}
Summary:	Wrapper around OVH's APIs

License:	3-clause BSD
URL:		http://api.ovh.com
Source0:	https://github.com/ovh/%{name}/archive/v%{version}.tar.gz


BuildArch:	noarch
BuildRequires:	python-devel
BuildRequires:	python-setuptools
BuildRequires:	python-sphinx

%if %{with python3}
BuildRequires:	python3-devel
BuildRequires:	python3-setuptools
%endif

%package -n python2-%{pypi_name}
Summary:	%{summary}
%{?python_provide:%python_provide python2-%{pypi_name}}
Requires:	python2-setuptools

%description -n python2-%{pypi_name}
%description
Lightweight wrapper around OVH's APIs. Handles all the hard work including credential creation and requests signing. This package provides Python 2 module bindings only.

%if %{with python3}
%package -n python3-%{pypi_name}
Summary:	%{summary}
%{?python_provide:%python_provide python3-%{pypi_name}}
Requires:	python3-setuptools

%description -n python3-%{pypi_name}
Lightweight wrapper around OVH's APIs. Handles all the hard work including credential creation and requests signing. This package provides Python 3 module bindings only.
%endif


%prep
%autosetup -n %{name}-%{version}
rm -rf %{name}.egg-info


%build
%py2_build
%if %{with python3}
%py3_build
%endif


%install
rm -rf $RPM_BUILD_ROOT
%if %{with python3}
%py3_install
%endif
%py2_install
# cd docs && make html

%check
%if 0%{with_test}
%{__python2} setup.py test
%if %{with python3}
%{__python3} setup.py test
%endif 
%endif


%files -n python2-%{pypi_name}
%doc README.rst CONTRIBUTING.rst CHANGELOG.md MIGRATION.rst
%doc examples
%license LICENSE
%{python2_sitelib}/*

%if %{with python3}
%files -n python3-%{pypi_name}
%doc README.rst CONTRIBUTING.rst CHANGELOG.md MIGRATION.rst
%doc examples 
%license LICENSE
%{python3_sitelib}/*
%endif


%changelog
* Fri Sep 15 2017 Geoffrey Bauduin <geoffrey.bauduin@corp.ovh.com> - 0.4.8-1
  - New upstream release v0.4.8
  - [feature] Add ResourceExpiredError exception (#48)
