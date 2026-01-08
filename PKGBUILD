# Maintainer: Evil Crow RF TUI Project
pkgname=evilcrow-tui-git
pkgver=r1.2458c4d
pkgrel=1
pkgdesc="TUI (Text User Interface) for Evil Crow RF V2 (Git version)"
arch=('any')
url="https://github.com/marceloapd/evilcrow-rf-tui"
license=('GPL3')
depends=('python' 'python-pyserial' 'python-textual' 'python-rich' 'platformio-core')
makedepends=('git' 'python-build' 'python-installer' 'python-wheel' 'python-setuptools')
optdepends=(
    'esptool: for flashing firmware manually'
    'screen: for serial monitoring'
)
provides=('evilcrow-tui')
conflicts=('evilcrow-tui')
source=("$pkgname::git+$url.git")
sha256sums=('SKIP')

pkgver() {
    cd "$srcdir/$pkgname"
    printf "r%s.%s" "$(git rev-list --count HEAD)" "$(git rev-parse --short HEAD)"
}

build() {
    cd "$srcdir/$pkgname/tui"
    python -m build --wheel --no-isolation
}

package() {
    cd "$srcdir/$pkgname"

    # Install Python TUI
    cd tui
    python -m installer --destdir="$pkgdir" dist/*.whl

    # Install firmware files
    cd ../firmware
    install -dm755 "$pkgdir/usr/share/$pkgname/firmware"
    cp -r src platformio.ini "$pkgdir/usr/share/$pkgname/firmware/"

    # Install scripts
    cd ..
    install -dm755 "$pkgdir/usr/share/$pkgname/scripts"
    install -Dm755 scripts/flash_firmware.sh "$pkgdir/usr/share/$pkgname/scripts/"
    install -Dm755 scripts/test_serial.py "$pkgdir/usr/share/$pkgname/scripts/"
    [ -f scripts/test_jammer.py ] && install -Dm755 scripts/test_jammer.py "$pkgdir/usr/share/$pkgname/scripts/" || true
    [ -f scripts/test_scanner.py ] && install -Dm755 scripts/test_scanner.py "$pkgdir/usr/share/$pkgname/scripts/" || true
    [ -f scripts/test_tx.py ] && install -Dm755 scripts/test_tx.py "$pkgdir/usr/share/$pkgname/scripts/" || true

    # Install documentation
    install -Dm644 README.md "$pkgdir/usr/share/doc/$pkgname/README.md"

    # Install udev rules for USB access
    install -Dm644 /dev/stdin "$pkgdir/usr/lib/udev/rules.d/99-evilcrow.rules" <<EOF
# Evil Crow RF V2 USB device rules
SUBSYSTEM=="tty", ATTRS{idVendor}=="10c4", ATTRS{idProduct}=="ea60", MODE="0666", GROUP="uucp"
SUBSYSTEM=="tty", ATTRS{idVendor}=="1a86", ATTRS{idProduct}=="7523", MODE="0666", GROUP="uucp"
EOF

    # Post-install message
    install -Dm644 /dev/stdin "$pkgdir/usr/share/$pkgname/post-install.txt" <<EOF
Evil Crow RF V2 TUI installed successfully!

Next steps:
1. Add your user to the uucp group:
   sudo usermod -a -G uucp \$USER

2. Reload udev rules:
   sudo udevadm control --reload-rules
   sudo udevadm trigger

3. Logout and login again (or reboot)

4. Flash firmware:
   cd /usr/share/$pkgname/firmware
   pio run --target upload

5. Run TUI:
   evilcrow

For more info: https://github.com/you/evilcrow-rf-tui
EOF
}
