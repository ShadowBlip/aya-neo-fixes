# Maintainer: Derek J. Clark <derekjohn dot clark at gmail dot com>
pkgname=aya-neo-fixes-git
pkgver=1.0.0
pkgrel=1
pkgdesc="Various fixes for the Aya Neo 2021/Pro on systems using systemd"
arch=('x86_64')
url="https://github.com/ShadowBlip/aya-neo-fixes"
license=('GPL')
groups=()
depends=('systemd-suspend-modules')
makedepends=()
optdepends=()
provides=()
conflicts=()
replaces=()
backup=()
options=()
install="./install.sh"
changelog=
source=(./)
noextract=()
md5sums=() #autofill using updpkgsums

build() {
  cd "$pkgname-$pkgver"

  ./configure --prefix=/usr
  make
}

package() {
  cd "$pkgname-$pkgver"

  make DESTDIR="$pkgdir/" install
}
