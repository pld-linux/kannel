Summary:	A catchy.net initiative to deliver a full-featured WAP browser
Summary(pl):	Bramka WAP oraz SMS
Name:		kannel
Version:	1.2.0
Release:	1
License:	BSD
Group:		Networking/Daemons
Source0:	http://www.kannel.org/download/1.2.0/gateway-1.2.0.tar.gz
Source1:	%{name}.init
URL:		http://www.kannel.org/
BuildRequires:	ImageMagick
BuildRequires:	jade
BuildRequires:	libxml2-devel
BuildRequires:	mysql-devel
BuildRequires:	openssl-devel
Requires(post,preun):	/sbin/chkconfig
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%description
WAP gateway.

%description -l pl
Bramka WAP.

%prep
%setup -q -n gateway-%{version}

%build
%configure2_13 \
	--enable-cookies \
	--with-ssl=%{_prefix} \
	--enable-mysql \
	--with-wtls=openssl

touch .depend
%{__make} depend
%{__make}

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT%{_sysconfdir}/rc.d/init.d
install -d $RPM_BUILD_ROOT{%{_bindir},%{_sbindir}}
install -d $RPM_BUILD_ROOT%{_mandir}/man{1,5,8}
install -d $RPM_BUILD_ROOT/home/httpd/html

install mini_httpd	$RPM_BUILD_ROOT%{_sbindir}
install	htpasswd	$RPM_BUILD_ROOT%{_bindir}/mini-htpasswd
install *.1		$RPM_BUILD_ROOT%{_mandir}/man1
install *.8		$RPM_BUILD_ROOT%{_mandir}/man8

install index.html	$RPM_BUILD_ROOT/home/httpd/html
install %{SOURCE1}	$RPM_BUILD_ROOT%{_sysconfdir}/rc.d/init.d/%{name}

%clean
rm -rf $RPM_BUILD_ROOT

%post
/sbin/chkconfig --add %{name}

%preun
if [ "$1" = "0" ]; then
	/etc/rc.d/init.d/%{name} stop
	/sbin/chkconfig --del %{name}
fi

%files
%defattr(644,root,root,755)
%doc README
%attr(755,root,root) %{_bindir}/*
%attr(755,root,root) %{_sbindir}/*
/home/httpd/html/index.html
%attr(755,root,root) /etc/rc.d/init.d/mini_httpd
%{_mandir}/man*/*
