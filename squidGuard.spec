Summary: Filter, redirector and access controller plugin for Squid. 
Name: squidGuard
Version: 1.1.4
Release: 12mdk
License: GPL
Group: System/Servers
Source0:  ftp://ftp.ost.eltele.no/pub/www/proxy/squidGuard/squidGuard-%{version}.tar.bz2
Source1:  %{name}.conf.sample
Source2:  blacklists-readme
Source3:  %{name}.cgi
Source4:  nulbanner.png
URL: http://www.squidguard.org
Patch0: squidGuard-%{version}.patch.bz2
Patch1: squidGuard-%{version}.default_dir.patch.bz2
BuildRoot: %{_tmppath}/%{name}-%{version}-root
BuildRequires: BerkeleyDB-devel = 2.7.7
Requires: squid

%description
SquidGuard is a combined filter, redirector and access controller plugin for
Squid. It is free, very flexible, extremely fast, easily installed, portable.
SquidGuard can be used to 
- limit the web access for some users to a list of accepted/well known web
servers and/or URLs only. 
- block access to some listed or blacklisted web servers and/or URLs for
some users. 
- block access to URLs matching a list of regular expressions or words for
some users. 
- enforce the use of domainnames/prohibit the use of IP address in URLs. 
- redirect blocked URLs to an "intelligent" CGI based info page.
- redirect unregistered user to a registration form. 
- redirect popular downloads like Netscape, MSIE etc. to local copies. 
- redirect banners to an empty GIF.
- have different access rules based on time of day, day of the week, date
etc. 
- have different rules for different user groups. 


Neither squidGuard nor Squid can be used to 

- filter/censor/edit text inside documents 
- filter/censor/edit embeded scripting languages 
  like JavaScript or VBscript inside HTML 


%prep

%setup -q
%patch0 -p1
%patch1 -p1

%build

CFLAGS="$RPM_OPT_FLAGS" 
%configure \
	--with-db-lib=%{_libdir}/BerkeleyDB \
	--with-db-inc=%{_includedir}/BerkeleyDB \

make
#make test

%install
rm -rf $RPM_BUILD_ROOT

P=$RPM_BUILD_DIR/%{name}-%{version}
Q=$RPM_BUILD_ROOT/%{_datadir}/%{name}-%{version}

%makeinstall

strip $RPM_BUILD_ROOT/%{_bindir}/* $RPM_BUILD_ROOT/%{_bindir}/*

mkdir -p $Q/{contrib,samples,log}

# the mandrake default config directories
mkdir -p $Q/db/{advertising,bannedsource,banneddestination}
mkdir -p $Q/db/{timerestriction,lansource,privilegedsource}

touch $Q/db/advertising/{domains,urls}
touch $Q/db/banneddestination/{domains,urls,expressions}
touch $Q/db/bannedsource/ips
touch $Q/db/lansource/lan
touch $Q/db/timerestriction/lan
touch $Q/db/privilegedsource/ips

# the blacklists default directories (Fabrice Pringent's one)
mkdir -p $Q/db/{porn,adult,audio-video,forums,hacking,redirector}
mkdir -p $Q/db/{warez,ads,aggressive,drugs,gambling,publicite,violence}
touch $Q/db/porn/{domains,urls,expressions}
touch $Q/db/adult/{domains,urls,expressions}
touch $Q/db/audio-video/{domains,urls}
touch $Q/db/forums/{domains,urls,expressions}
touch $Q/db/hacking/{domains,urls}
touch $Q/db/redirector/{domains,urls,expressions}
touch $Q/db/warez/{domains,urls}
touch $Q/db/ads/{domains,urls}
touch $Q/db/aggressive/{domains,urls}
touch $Q/db/drugs/{domains,urls}
touch $Q/db/gambling/{domains,urls}
touch $Q/db/publicite/{domains,urls,expressions}
touch $Q/db/violence/{domains,urls,expressions}

cd $P/samples/dest/
tar xzf blacklists.tar.gz
cp -af blacklists/* $Q/db
cd -

cp -a $P/contrib/hostbyname/hostbyname $Q/contrib/
cp -a $P/contrib/sgclean/sgclean $Q/contrib/
cp -a $P/contrib/squidGuardRobot/{squidGuardRobot,RobotUserAgent.pm} $Q/contrib/

cp -a $P/samples/dest $Q/samples
#cp -a $P/samples/*{.conf,.cgi} $Q/samples
cp -a %{SOURCE2} $P/

rm -rf $Q/test/test*.conf.*

# default config files
#log & error files
mkdir -p $RPM_BUILD_ROOT/var/log/%{name}
touch $RPM_BUILD_ROOT/var/log/%{name}/%{name}.{log,error}

#conf file
mkdir -p $RPM_BUILD_ROOT/etc/squid
install %{SOURCE1} $RPM_BUILD_ROOT/etc/squid/%{name}.conf.sample
cp -af %{SOURCE3} %{SOURCE4} $Q/samples

%post
echo "WARNING !!! WARNING !!! WARNING !!! WARNING !!!"
echo ""
echo "Modify the following line in the /etc/squid/squid.conf file:"
echo "redirect_program /usr/bin/squidGuard -c /etc/squid/squidGuard.conf"

%clean
rm -rf $RPM_BUILD_ROOT

%files
%defattr(-,root,root)
%doc README ANNOUNCE GPL COPYING blacklists-readme doc/*.{html,gif,txt}
%{_bindir}/*
%{_datadir}/%{name}-%{version}/contrib/*
%{_datadir}/%{name}-%{version}/samples/*.cgi
%{_datadir}/%{name}-%{version}/samples/*.png
%attr(0755,root,root) %{_datadir}/%{name}-%{version}/db/*
%attr(-,squid,squid)/var/log/%{name}/*
%config(noreplace) /etc/squid/*

%changelog
* Wed Jul 11 2001 Florin <florin@mandrakesoft.com> 1.1.4-12mdk
- use the new sample configfile blacklist compliant, logs and data locations
- patch the default logdir and confdir (default_dir.patch)
- add the blacklists-readme file
- add the blacklist sections and databases
- remove the whole test thing from the spec file
- add the nullbanner.png and the squidGuard.cgi modified

* Fri Feb 16 2001 Florin <florin@mandrakesoft.com> 1.1.4-11mdk
- add banneddestination/expressions

* Tue Jan 30 2001 Florin <florin@mandrakesoft.com> 1.1.4-10mdk
- add the timerestriction section

* Tue Jan 30 2001 Florin <florin@mandrakesoft.com> 1.1.4-9mdk
- the nulbanner and the cgi go now in the httpd-naat package
- add /etc/squid/squidGuard.conf.sample
- create the section files from the default config file

* Wed Jan 24 2001 Florin <florin@mandrakesoft.com> 1.1.4-9mdk
- add the nulbanner.gif in the /var/www-naat/icons

* Mon Jan 08 2001 Florin <florin@mandrakesoft.com> 1.1.4-8mdk
- the /var/log/%{name} dir is now owned by squid,squid

* Fri Jan 06 2001 Florin <florin@mandrakesoft.com> 1.1.4-7mdk
- recompile for firewall distrib
- add log,error files in /var/log/%{name}
- copy a sample of the config file in the /etc/squid/directory

* Thu Nov 23 2000 Florin <florin@mandrakesoft.com> 1.1.4-6mdk
- added urls (Lenny compliant ;)

* Thu Nov 23 2000 Florin <florin@mandrakesoft.com> 1.1.4-5mdk
- requires squid
- buildrequires BerkeleyDB

* Tue Nov 21 2000 Florin <florin@mandrakesoft.com> 1.1.4-4mdk
- requires BerkeleyDB package, the new db2-2.7.7 package
- comment the postun section

* Mon Sep 18 2000 Florin <florin@mandrakesoft.com> 1.1.4-3mdk
- set up a ready to use out of the box config

* Fri Sep 15 2000 Florin <florin@mandrakesoft.com> 1.1.4-2mdk
- added the test configuration and the Makefile
- modifying the config files

* Fri Sep 15 2000 Florin <florin@mandrakesoft.com> 1.1.4-1mdk
- first attempt
