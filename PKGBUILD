# Maintainer: Andre
pkgname=decman-git
pkgver=0.3.4
pkgrel=1
pkgdesc="Declarative package & configuration manager for Arch Linux"
arch=('any')
url="https://github.com/tripleducky/decman"
license=('custom')
depends=('python' 'python-requests' 'pacman' 'devtools')
makedepends=('python-build' 'python-installer' 'python-setuptools')
source=()
md5sums=()

pkgver() {
    cd "$startdir"
    grep '^version = ' pyproject.toml | cut -d'"' -f2
}

build() {
    python -m build --wheel --no-isolation
    cd "$startdir"
}

package() {
    cd "$startdir"
    python -m installer --destdir="$pkgdir" dist/*.whl
    
    # Install license if it exists
    if [ -f LICENSE ]; then
        install -Dm644 LICENSE "$pkgdir/usr/share/licenses/$pkgname/LICENSE"
    fi
}
