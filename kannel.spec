# TODO:
# - upgrade to 1.2.2
# - check file list when built with docs
#
# Conditional build:
%bcond_with	doc		# build documentation
%bcond_with	openssl		# link against openssl (requires multithreaded libs)
%bcond_without	mysql		# don't link against mysql
#
Summary:	SMS/WAP gateway
Summary(pl):	Bramka WAP oraz SMS
Name:		kannel
Version:	1.2.0
Release:	5
License:	BSD-like (see COPYING)
Group:		Networking/Daemons
Source0:	http://www.kannel.org/download/%{version}/gateway-%{version}.tar.gz
# Source0-md5:	963502f15909ff3e53f5f7b2d8bdb218
Source1:	%{name}.init
Source2:	%{name}.sysconfig
Source3:	%{name}.conf
Patch0:		%{name}-types.patch
Patch1:		%{name}-nolibs.patch
URL:		http://www.kannel.org/
BuildRequires:	ImageMagick
BuildRequires:	libxml2-devel
BuildRequires:	autoconf
%{?with_mysql:BuildRequires:	mysql-devel}
%{?with_doc:BuildRequires:	openjade}
# requires multithread enabled openssl (?)
%{?with_openssl:BuildRequires:	openssl-devel >= 0.9.7d}
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
Kannel jest bramk± SMS/WAP Open Source. WAP pozwala u¿ywaæ telefonów
jako prostych przegl±darek hipertekstowych, ale korzysta ze
zoptymalizowanych protoko³ów transmisji. Bramka WAP t³umaczy je na
protoko³y internetowe. Kannel dzia³a równie¿ jako bramka SMS dla sieci
GSM. Prawie wszystkie telefony GSM mog± odbieraæ i wysy³aæ wiadomo¶ci
SMS, wiêc pozwala to na obs³ugê wiêkszej liczby klientów.

%prep
%setup -q -n gateway-%{version}
%patch0 -p1
%patch1 -p1

%build
%{__autoconf}
%configure \
	--with-malloc-native \
	--enable-cookies \
	--%{?with_mysql:en}%{!?with_mysql:dis}able-mysql \
	%{?with_openssl: --with-wtls=openssl --with-ssl=%{_prefix} --en}%{!?with_openssl: --dis}able-ssl \
	--%{!?with_doc:dis}%{?with_doc:en}able-docs

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
