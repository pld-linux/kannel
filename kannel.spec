#
# Conditional build:
# _with_docs		- build documentation
# _with_openssl		- link against openssl (requires multithreaded libs)
# _without_mysql	- don't link against mysql
#
# TODO:
# - upgrade to 1.2.2
# - check file list when built with docs

Summary:	SMS/WAP gateway
Summary(pl):	Bramka WAP oraz SMS
Name:		kannel
Version:	1.2.0
Release:	4
License:	BSD-like (see COPYING)
Group:		Networking/Daemons
Source0:	http://www.kannel.org/download/%{version}/gateway-%{version}.tar.gz
# Source0-md5:	963502f15909ff3e53f5f7b2d8bdb218
Source1:	%{name}.init
Source2:	%{name}.sysconfig
Source3:	%{name}.conf
URL:		http://www.kannel.org/
BuildRequires:	ImageMagick
BuildRequires:	libxml2-devel
%{!?_without_mysql:BuildRequires:	mysql-devel}
%{?_with_docs:BuildRequires:	openjade}
# requires multithread enabled openssl (?)
%{?_with_openssl:BuildRequires:		openssl-devel}
BuildRequires:	zlib-devel
Requires(post,preun):	/sbin/chkconfig
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%description
Kannel is an Open Source SMS/WAP gateway. WAP is short for Wireless
Application Protocol. It lets the phone act as a simple hypertext
browser, but optimizes the markup language, scripting language, and
the transmission protocols for wirelessuse. The optimized protocols
are translated to normal Internet protocols by a WAP gateway. Kannel
also works as a SMS gateway for GSM networks. Almost all GSM phones
can send and receive SMS messages, so this is a way to serve many more
clients than just those using WAP phones.

%description -l pl
Kannel jest bramk� SMS/WAP Open Source. WAP pozwala u�ywa� telefon�w
jako prostych przegl�darek hipertekstowych, ale korzysta ze
zoptymalizowanych protoko��w transmisji. Bramka WAP t�umaczy je na
protoko�y internetowe. Kannel dzia�a r�wnie� jako bramka SMS dla sieci
GSM. Prawie wszystkie telefony GSM mog� odbiera� i wysy�a� wiadomo�ci
SMS, wi�c pozwala to na obs�ug� wi�kszej liczby klient�w.

%prep
%setup -q -n gateway-%{version}

%build
%configure2_13 \
	--with-malloc-native \
	--enable-cookies \
	--%{!?_without_mysql:en}%{?_without_mysql:dis}able-mysql \
	%{?_with_openssl: --with-wtls=openssl --with-ssl=%{_prefix} --en}%{!?_with_openssl: --dis}able-ssl \
	--%{!?_with_docs:dis}%{?_with_docs:en}able-docs

touch .depend
%{__make} depend
%{__make}

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT{%{_bindir},%{_sbindir},%{_mandir}/man{1,8}}

%{__make} install \
	DESTDIR=$RPM_BUILD_ROOT

install -D %{SOURCE1}	$RPM_BUILD_ROOT%{_sysconfdir}/rc.d/init.d/%{name}
install -D %{SOURCE2}	$RPM_BUILD_ROOT%{_sysconfdir}/sysconfig/%{name}
install -D %{SOURCE3}	$RPM_BUILD_ROOT%{_sysconfdir}/kannel/%{name}.conf
install gw/smskannel.conf $RPM_BUILD_ROOT%{_sysconfdir}/kannel/smskannel.conf
install test/fakesmsc $RPM_BUILD_ROOT%{_bindir}
install test/fakewap $RPM_BUILD_ROOT%{_bindir}

%clean
rm -rf $RPM_BUILD_ROOT

%post
if [ "$1" = "1" ]; then
	/sbin/chkconfig --add %{name}
	echo "Run \"/etc/rc.d/init.d/kannel start\" to start kannel." >&2
else
	if [ -f /var/lock/subsys/kannel ]; then
		/etc/rc.d/init.d/kannel restart >&2
	fi
fi


%preun
if [ "$1" = "0" ]; then
	if [ -f /var/lock/subsys/kannel ]; then
		/etc/rc.d/init.d/kannel stop >&2
	fi
	/sbin/chkconfig --del kannel
fi

%files
%defattr(644,root,root,755)
%doc README COPYING NEWS VERSION STATUS doc/{dialup.txt,dlr-mysql.conf,kannel.conf,modems.conf}
%attr(755,root,root) %{_bindir}/*
%attr(755,root,root) %{_sbindir}/*
%attr(754,root,root) /etc/rc.d/init.d/%{name}
%config(noreplace) %verify(not size mtime md5) %{_sysconfdir}/sysconfig/%{name}
%config(noreplace) %verify(not size mtime md5) %{_sysconfdir}/kannel/kannel.conf
%config(noreplace) %verify(not size mtime md5) %{_sysconfdir}/kannel/smskannel.conf
%dir %{_sysconfdir}/kannel
%{_mandir}/man*/*
