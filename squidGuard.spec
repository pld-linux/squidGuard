%define		blist_ver 20051119
%define		ver 1.4
Summary:	Filter, redirector and access controller plugin for Squid
Summary(pl.UTF-8):	Wtyczka z filtrem, przekierowywaniem i kontrolerem dostępu dla Squida
Name:		squidGuard
Version:	%{ver}_%{blist_ver}
Release:	4
Epoch:		2
License:	GPL
Group:		Networking/Daemons
Source0:	http://squidguard.org/Downloads/squidGuard-%{ver}.tar.gz
# Source0-md5:	de834150998c1386c30feae196f16b06
Source1:	%{name}.conf
Source2:	ftp://ftp.teledanmark.no/pub/www/proxy/squidGuard/contrib/blacklists-%{blist_ver}.tar.gz
# Source2-md5:	7ebb53ea33459c14cbc850cd73405915
# http://www.squidguard.org/Downloads/Patches/1.4/squidGuard-1.4-patch-20091015.tar.gz
Patch0:		%{name}-long-urls-buffer-overflow.patch
Patch1:		%{name}-url-bypass.patch
URL:		http://www.squidguard.org/
BuildRequires:	autoconf
BuildRequires:	automake
BuildRequires:	db-devel
BuildRequires:	flex
BuildRequires:	gettext-tools
BuildRequires:	libtool
BuildRequires:	rpmbuild(macros) >= 1.268
Requires(post):	grep
Requires(post,preun):	squid
Requires(postun):	sed >= 4.0
Requires:	squid
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%define		_sysconfdir	/etc/%{name}
%define		_datadir	%{_sysconfdir}

%description
SquidGuard is a combined filter, redirector and access controller
plugin for Squid. It is free, very flexible, extremely fast, easily
installed, portable. SquidGuard can be used to:
- limit the web access for some users to a list of accepted/well known
  web servers and/or URLs only,
- block access to some listed or blacklisted web servers and/or URLs
  for some users,
- block access to URLs matching a list of regular expressions or words
  for some users,
- enforce the use of domainnames/prohibit the use of IP address in
  URLs,
- redirect blocked URLs to an "intelligent" CGI based info page,
- redirect unregistered user to a registration form,
- redirect popular downloads like Netscape, MSIE etc. to local copies,
- redirect banners to an empty GIF,
- have different access rules based on time of day, day of the week,
  date etc,
- have different rules for different user groups.

Neither squidGuard nor Squid can be used to:
- filter/censor/edit text inside documents,
- filter/censor/edit embeded scripting languages like JavaScript or
  VBscript inside HTML.

%description -l pl.UTF-8
SquidGuard jest wtyczką dla Squida będącą połączonym filtrem,
przekierowywaniem i kontrolerem dostępu. Jest darmowy, elastyczny,
bardzo szybki, łatwo instalowalny, przenośny. Może być używany do:
- ograniczenia dostępu do WWW dla niektórych użytkowników na podstawie
  listy akceptowanych serwerów lub URL-i,
- blokowania dostępu do niektórych serwerów lub URL-i dla niektórych
  użytkowników,
- blokowania dostępu do URL na podstawie wyrażeń regularnych lub słów
  dla niektórych użytkowników,
- narzucenia używania nazw domen/zabronienia używania adresów IP w
  URL-ach,
- przekierowania zablokowanych URL-i na "inteligentną" stronę
  informacyjną w CGI,
- przekierowania niezarejestrowanych użytkowników do formularza
  rejestracyjnego,
- przekierowania ściągania popularnego oprogramowania (Netscape, MSIE)
  na lokalne kopie,
- przekierowania bannerów na puste GIF-y,
- uzależnienia reguł dostępu w zależności od pory dnia, dnia tygodnia,
  daty itp.,
- różnych reguł dostępu dla różnych grup użytkowników.

Natomiast ani squidGuard ani Squid nie może być użyty do:
- filtrowania/cenzurowania/edycji tekstu wewnątrz dokumentu,
- filtrowania/cenzurowania/edycji osadzonych w HTML skryptów
  (JavaScript, VBscript...)

%prep
%setup -q -n %{name}-%{ver}
%patch -P0 -p1
%patch -P1 -p1

%build
%{__libtoolize}
%{__gettextize}
%{__aclocal}
%{__autoconf}
%configure \
	--with-sg-logdir=/var/log/%{name} \
	--with-sg-config=%{_sysconfdir}/squidGuard.conf \
	--with-sg-dbhome=%{_sysconfdir}/db \
	--with-db=%{_prefix}

%{__make}

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT{/var/log/%{name},%{_bindir}} \
	$RPM_BUILD_ROOT%{_sysconfdir}/db/{advertising,bannedsource,banneddestination} \
	$RPM_BUILD_ROOT%{_sysconfdir}/db/{timerestriction,lansource,privilegedsource}

install src/squidGuard $RPM_BUILD_ROOT%{_bindir}

touch $RPM_BUILD_ROOT%{_sysconfdir}/db/advertising/{domains,urls}
touch $RPM_BUILD_ROOT%{_sysconfdir}/db/banneddestination/{domains,urls,expressions}
touch $RPM_BUILD_ROOT%{_sysconfdir}/db/bannedsource/ips
touch $RPM_BUILD_ROOT%{_sysconfdir}/db/lansource/lan
touch $RPM_BUILD_ROOT%{_sysconfdir}/db/timerestriction/lan
touch $RPM_BUILD_ROOT%{_sysconfdir}/db/privilegedsource/ips

touch $RPM_BUILD_ROOT/var/log/%{name}/%{name}.{log,error}

tar zxf %{SOURCE2} -C $RPM_BUILD_ROOT%{_sysconfdir}/db
install %{SOURCE1} $RPM_BUILD_ROOT%{_sysconfdir}
rm -rf samples/dest

rm -f $(find $RPM_BUILD_ROOT%{_sysconfdir}/db -name *diff -type f)

%clean
rm -rf $RPM_BUILD_ROOT

%post
if [ -f /etc/squid/squid.conf ] && \
	! grep -q "^redirect_program.*%{_bindir}/%{name}" /etc/squid/squid.conf; then
	echo "redirect_program %{_bindir}/squidGuard -c /etc/squidGuard/squidGuard.conf" >>/etc/squid/squid.conf
	%service -q squid reload
fi

%preun
if [ -f /etc/squid/squid.conf ]; then
	%{__sed} -i -e /^redirect_program.*%(echo %{_bindir}/%{name} | sed -e 's,/,\\/,g')/d' /etc/squid/squid.conf
	#' spec.vim sucks
	%service -q squid reload
fi

%files
%defattr(644,root,root,755)
%doc README ANNOUNCE samples/* doc/*.{html,gif,txt}
%doc contrib/{squidGuardRobot/{squidGuardRobot,RobotUserAgent.pm},sgclean/sgclean,hostbyname/hostbyname}
%attr(755,root,root) %{_bindir}/*
%attr(750,root,squid) %dir %{_sysconfdir}
%attr(640,root,squid) %config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/squidGuard.conf
%{_sysconfdir}/db
%attr(770,root,squid) %dir /var/log/%{name}
%attr(640,squid,squid) %ghost /var/log/%{name}/*
