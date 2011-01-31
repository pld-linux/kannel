# TODO:
# - check file list when built with docs
#
# Conditional build:
%bcond_with	doc		# build documentation
%bcond_without	openssl		# link against openssl (requires multithreaded libs)
%bcond_without	mysql		# don't link against mysql
#
Summary:	SMS/WAP gateway
Summary(pl.UTF-8):	Bramka WAP oraz SMS
Name:		kannel
Version:	1.4.3
Release:	4
License:	BSD-like (see COPYING)
Group:		Networking/Daemons
Source0:	http://www.kannel.org/download/%{version}/gateway-%{version}.tar.gz
# Source0-md5:	8925b147fb7aa01a10fa4f53cfeb03e9
Source1:	%{name}.init
Source2:	%{name}.sysconfig
Source3:	%{name}.conf
Patch0:		%{name}-types.patch
Patch1:		%{name}-nolibs.patch
URL:		http://www.kannel.org/
BuildRequires:	ImageMagick
BuildRequires:	autoconf
BuildRequires:	automake
BuildRequires:	libxml2-devel
BuildRequires:	pcre-devel
BuildRequires:	pam-devel
%{?with_mysql:BuildRequires:	mysql-devel}
%if %{with doc}
BuildRequires:	openjade
BuildRequires:	texlive-latex
BuildRequires:	texlive-latex-ams
BuildRequires:	texlive-latex-extend
%endif
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

%description -l pl.UTF-8
Kannel jest bramką SMS/WAP Open Source. WAP pozwala używać telefonów
jako prostych przeglądarek hipertekstowych, ale korzysta ze
zoptymalizowanych protokołów transmisji. Bramka WAP tłumaczy je na
protokoły internetowe. Kannel działa również jako bramka SMS dla sieci
GSM. Prawie wszystkie telefony GSM mogą odbierać i wysyłać wiadomości
SMS, więc pozwala to na obsługę większej liczby klientów.

%prep
%setup -q -n gateway-%{version}
%patch0 -p1
#%patch1 -p1

%build
cp -f /usr/share/automake/config.sub .
%{__autoconf}
%configure \
	CFLAGS="%{rpmcppflags} %{rpmcflags}" \
	--with-malloc=native \
	--enable-cookies \
	--enable-pcre \
	--enable-pam \
	--with%{!?with_mysql:out}-mysql \
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

install -D %{SOURCE1}	$RPM_BUILD_ROOT/etc/rc.d/init.d/%{name}
install -D %{SOURCE2}	$RPM_BUILD_ROOT/etc/sysconfig/%{name}
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
%doc LICENSE README COPYING NEWS VERSION STATUS doc/{*.txt,examples/*.conf}
%doc doc/ChangeLog*
%attr(755,root,root) %{_bindir}/*
%attr(755,root,root) %{_sbindir}/*
%attr(754,root,root) /etc/rc.d/init.d/%{name}
%config(noreplace) %verify(not md5 mtime size) /etc/sysconfig/%{name}
%config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/kannel/kannel.conf
%config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/kannel/smskannel.conf
%dir %{_sysconfdir}/kannel
%{_mandir}/man*/*
