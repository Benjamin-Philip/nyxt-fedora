#
# spec file for package nyxt
#
# Copyright (c) 2022 SUSE LLC
#
# All modifications and additions to the file contributed by third parties
# remain the property of their copyright owners, unless otherwise agreed
# upon. The license for this file, and modifications and additions to the
# file, is the same license as for the pristine package itself (unless the
# license for the pristine package is not an Open Source License, in which
# case the license is the MIT License). An "Open Source License" is a
# license that conforms to the Open Source Definition (Version 1.9)
# published by the Open Source Initiative.

# Please submit bugfixes or comments via https://bugs.opensuse.org/
#


# WebExtension support is not included by default because it's unfinished
# and possibly prone to security issues.
%bcond_with webextensions

# In case we want to use a pre-release
%global rel -pre-release-5

# To ignore the empty debugfiles.list file
%global debug_package %{nil}

Name:           nyxt
Version:        3
Release:        0
Summary:        Keyboard-oriented, Common Lisp extensible web-browser
License:        BSD-3-Clause
Group:          Productivity/Networking/Web/Browsers
URL:            https://nyxt.atlas.engineer
Source:         https://github.com/atlas-engineer/nyxt/releases/download/%{version}%{rel}/nyxt-%{version}-source-with-submodules.tar.xz
Requires:       libwebkit2gtk-4_1-0
Requires:       libfixposix4
Requires:       enchant-tools
Requires:       glib-networking
Requires:       gsettings-desktop-schemas
Requires:       xclip
BuildRequires:  pkgconfig(libfixposix)
BuildRequires:  gobject-introspection
BuildRequires:  pkgconfig(webkit2gtk-4.1)
Buildrequires:  pkgconfig(libcrypto)
BuildRequires:  sbcl
BuildRequires:  gcc-c++
BuildRequires:  git

%description
Nyxt is a keyboard-oriented, extensible web-browser designed for power users. It has familiar key-bindings (Emacs, VI, CUA), is fully configurable and extensible in Lisp, and has powerful features for productive professionals.

%prep
%setup -q -c -n nyxt

%build

# Force SBCL to open these files as UTF-8 and not ASCII

sed -i 's/stream \*tld-data-path\*/stream *tld-data-path* :external-format :utf-8/g' _build/cl-tld/cl-tld.lisp
sed -i 's/stream file/stream file :external-format :utf-8/g' _build/trivial-mimes/mime-types.lisp

%if %{with webextensions}
make all web-extensions PREFIX=/usr LIBDIR=%{_libdir} NYXT_COMPRESS=T
%else
make all PREFIX=/usr LIBDIR=%{_libdir} NYXT_COMPRESS=T # LISP_FLAGS="--eval '(setf sb-impl::*default-external-format* :utf-8)'"
# following lines are a work-around for https://github.com/atlas-engineer/nyxt/issues/2624
rm nyxt
make all PREFIX=/usr LIBDIR=%{_libdir} NYXT_COMPRESS=T
%endif


%install

%make_install PREFIX=/usr LIBDIR=%{buildroot}/%{_libdir}

%if %{with webextensions}
strip -s %{buildroot}/%{_libdir}/nyxt/libnyxt.so
%endif

# create links to dynamycally loaded libfixposix.so and libwebkit2gtk-4.1.so
# in specific nyxt folder under libexecdir to avoid making this package depends
# on libfixposix and libwebkit2gtk-4.1 devel packages just for having the .so links
mkdir -p %{buildroot}/%{_libexecdir}/nyxt/

ln -s %{_libdir}/libfixposix.so.4 %{buildroot}/%{_libexecdir}/nyxt/libfixposix.so
ln -s %{_libdir}/libwebkit2gtk-4.1.so.0 %{buildroot}/%{_libexecdir}/nyxt/libwebkit2gtk-4.1.so

# wrap nyxt in a shell wrapper so it can find its dynamically loaded libs in libexecdir/nyxt
mv %{buildroot}/%{_bindir}/nyxt %{buildroot}/%{_bindir}/nyxt.bin

cat <<EOF >%{buildroot}/%{_bindir}/nyxt
#!/bin/sh
LD_LIBRARY_PATH=%{_libexecdir}/nyxt exec -a nyxt nyxt.bin "\$@"
EOF

chmod +x %{buildroot}/%{_bindir}/nyxt

%files
%{_bindir}/nyxt
%{_bindir}/nyxt.bin
%if %{with webextensions}
%{_libdir}/nyxt/
%endif
%{_libexecdir}/nyxt/
%{_datadir}/nyxt/
%{_datadir}/icons/hicolor/*/apps/nyxt.png
%{_datadir}/applications/nyxt.desktop
%doc README.org
%license licenses/ASSET-LICENSE
%license licenses/SOURCE-LICENSE

%changelog
