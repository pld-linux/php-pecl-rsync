#
# Conditional build:
%bcond_without	tests		# build without tests

%define		php_name	php%{?php_suffix}
%define		modname	rsync
Summary:	PHP extension for librsync
Name:		%{php_name}-pecl-%{modname}
Version:	0.1.0
Release:	2
License:	Modified BSD License
Group:		Development/Languages/PHP
Source0:	http://pecl.php.net/get/%{modname}-%{version}.tgz
# Source0-md5:	413189b50a5f458fdb6b5c011d3faa5f
URL:		http://pecl.php.net/package/rsync/
%{?with_tests:BuildRequires:    %{php_name}-cli}
BuildRequires:	%{php_name}-devel >= 4:5.2.6
BuildRequires:	librsync-devel
BuildRequires:	rpmbuild(macros) >= 1.666
%{?requires_php_extension}
Provides:	php(%{modname}) = %{version}
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%description
Include the posibility to PHP to generate signature files, patches and
patch files with the rsync functionality.

%prep
%setup -qc
mv %{modname}-%{version}/* .

rm -r librsync

%build
phpize
%configure \
	--with-rsync
%{__make}

%if %{with tests}
# simple module load test
%{__php} -n -q \
	-d extension_dir=modules \
	-d extension=%{modname}.so \
	-m > modules.log
grep %{modname} modules.log

export NO_INTERACTION=1 REPORT_EXIT_STATUS=1 MALLOC_CHECK_=2
%{__make} test \
	PHP_EXECUTABLE=%{__php}
%endif

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT%{php_sysconfdir}/conf.d
install -d $RPM_BUILD_ROOT{%{php_sysconfdir}/conf.d,%{php_extensiondir}}
install -d $RPM_BUILD_ROOT{%{php_sysconfdir}/conf.d,%{php_extensiondir},%{_examplesdir}/%{name}-%{version}}

%{__make} install \
	EXTENSION_DIR=%{php_extensiondir} \
	INSTALL_ROOT=$RPM_BUILD_ROOT

install -d $RPM_BUILD_ROOT%{php_sysconfdir}/conf.d
cat <<'EOF' > $RPM_BUILD_ROOT%{php_sysconfdir}/conf.d/%{modname}.ini
; Enable %{modname} extension module
extension=%{modname}.so
EOF

install -d $RPM_BUILD_ROOT%{_examplesdir}/%{name}-%{version}
cp -a examples/* $RPM_BUILD_ROOT%{_examplesdir}/%{name}-%{version}

%clean
rm -rf $RPM_BUILD_ROOT

%post
%php_webserver_restart

%postun
if [ "$1" = 0 ]; then
	%php_webserver_restart
fi

%files
%defattr(644,root,root,755)
%doc README TODO LICENSE
%config(noreplace) %verify(not md5 mtime size) %{php_sysconfdir}/conf.d/%{modname}.ini
%attr(755,root,root) %{php_extensiondir}/%{modname}.so
%{_examplesdir}/%{name}-%{version}
