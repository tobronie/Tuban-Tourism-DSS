<?php
include 'config.php';

// Check apakah tombol Matrix diklik
if (isset($_POST['matrix'])) {
    $data = mysqli_query($config, "SELECT * FROM m_matrixkeputusan");
    $judul_tabel = "Tabel Data Wisata (Matrix Keputusan)";
} elseif (isset($_POST['1'])) {
    $data = mysqli_query($config, "SELECT * FROM m_normalisasi_1");
    $judul_tabel = "Tabel Data Wisata (Normalisasi 1)";
} elseif (isset($_POST['2'])) {
    $data = mysqli_query($config, "SELECT * FROM m_normalisasi_2");
    $judul_tabel = "Tabel Data Wisata (Normalisasi 2)";
} elseif (isset($_POST['full'])) {
    $data = mysqli_query($config, "SELECT * FROM m_full");
    $judul_tabel = "Tabel Data Wisata (Full Multiplicative Form)";
} elseif (isset($_POST['rasio'])) {
    $data = mysqli_query($config, "SELECT * FROM m_rasio");
    $judul_tabel = "Tabel Data Wisata (Rasio)";
} else {
    // Default jika tidak ada tombol yang diklik
    $data = mysqli_query($config, "SELECT * FROM m_matrixkeputusan");
    $judul_tabel = "Data akan muncul, jika anda memilih tampilan data pada tombol";
}

?>

<!DOCTYPE html>
<html lang="en">
    <head>
        <meta charset="utf-8" />
        <meta http-equiv="X-UA-Compatible" content="IE=edge" />
        <meta name="viewport" content="width=device-width, initial-scale=1, shrink-to-fit=no" />
        <meta name="description" content="" />
        <meta name="author" content="" />
        <title>Matrix</title>
        <link href="https://cdn.jsdelivr.net/npm/simple-datatables@7.1.2/dist/style.min.css" rel="stylesheet" />
        <link href="css/styles.css" rel="stylesheet" />
        <script src="https://use.fontawesome.com/releases/v6.3.0/js/all.js" crossorigin="anonymous"></script>
    </head>
    <body class="sb-nav-fixed">
        <nav class="sb-topnav navbar navbar-expand navbar-dark bg-dark">
            <!-- Navbar Brand-->
            <a class="navbar-brand ps-3" href="index.php">Data Wisata</a>
            <!-- Sidebar Toggle-->
            <button class="btn btn-link btn-sm order-1 order-lg-0 me-4 me-lg-0" id="sidebarToggle" href="#!"><i class="fas fa-bars"></i></button>
            <!-- Navbar Search-->
            <form class="d-none d-md-inline-block form-inline ms-auto me-0 me-md-3 my-2 my-md-0">
                <div class="input-group">
                    <input class="form-control" type="text" placeholder="Search for..." aria-label="Search for..." aria-describedby="btnNavbarSearch" />
                    <button class="btn btn-primary" id="btnNavbarSearch" type="button"><i class="fas fa-search"></i></button>
                </div>
            </form>
            <!-- Navbar-->
            <ul class="navbar-nav ms-auto ms-md-0 me-3 me-lg-4">
                <li class="nav-item dropdown">
                    <a class="nav-link dropdown-toggle" id="navbarDropdown" href="#" role="button" data-bs-toggle="dropdown" aria-expanded="false"><i class="fas fa-user fa-fw"></i></a>
                    <ul class="dropdown-menu dropdown-menu-end" aria-labelledby="navbarDropdown">
                        <li><a class="dropdown-item" href="#!">Settings</a></li>
                        <li><a class="dropdown-item" href="#!">Activity Log</a></li>
                        <li><hr class="dropdown-divider" /></li>
                        <li><a class="dropdown-item" href="#!">Logout</a></li>
                    </ul>
                </li>
            </ul>
        </nav>
        <div id="layoutSidenav">
            <div id="layoutSidenav_nav">
            <nav class="sb-sidenav accordion sb-sidenav-dark" id="sidenavAccordion">
                    <div class="sb-sidenav-menu">
                        <div class="nav">
                            <div class="sb-sidenav-menu-heading">Data</div>
                            <a class="nav-link" href="index.php">
                                <div class="sb-nav-link-icon"><i class="fas fa-tachometer-alt"></i></div>
                                Dashboard
                            </a>
                            <a class="nav-link collapsed" href="#" data-bs-toggle="collapse" data-bs-target="#collapseLayouts" aria-expanded="false" aria-controls="collapseLayouts">
                                <div class="sb-nav-link-icon"><i class="fas fa-columns"></i></div>
                                Metode
                                <div class="sb-sidenav-collapse-arrow"><i class="fas fa-angle-down"></i></div>
                            </a>
                            <div class="collapse" id="collapseLayouts" aria-labelledby="headingOne" data-bs-parent="#sidenavAccordion">
                                <nav class="sb-sidenav-menu-nested nav">
                                    <a class="nav-link" href="result_saw.php">SAW</a>
                                    <a class="nav-link" href="result_wp.php">WP</a>
                                    <a class="nav-link" href="result_topsis.php">Topsis</a>
                                    <a class="nav-link" href="result_multimoora.php">Multimoora</a>
                                </nav>
                            </div>
                            <a class="nav-link collapsed" href="#" data-bs-toggle="collapse" data-bs-target="#collapseLayoutss" aria-expanded="false" aria-controls="collapseLayouts">
                                <div class="sb-nav-link-icon"><i class="fas fa-columns"></i></div>
                                Tampilan Data
                                <div class="sb-sidenav-collapse-arrow"><i class="fas fa-angle-down"></i></div>
                            </a>
                            <div class="collapse" id="collapseLayoutss" aria-labelledby="headingOne" data-bs-parent="#sidenavAccordion">
                                <nav class="sb-sidenav-menu-nested nav">
                                    <a class="nav-link" href="../Project/tampil/dataalternatif.php">Data Alternatif</a>
                                    <a class="nav-link" href="../Project/tampil/datakriteria.php">Data Kriteria</a>
                                    <a class="nav-link" href="../Project/tampil/databobot.php">Data Bobot</a>
                                    <a class="nav-link" href="../Project/tampil/dataskala.php">Data Skala</a>
                                    <a class="nav-link" href="../Project/tampil/datamatrix.php">Data Matrix</a>
                                </nav>
                            </div>
                        </div>
                    </div>
                    <div class="sb-sidenav-footer">
                        <div class="small">by:</div>
                        Imam Tobroni
                    </div>
                </nav>
            </div>
            <div id="layoutSidenav_content">
                <main>
                    <div class="container-fluid px-4">
                        <h1 class="mt-4">Detail Data Metode Multimoora</h1>
                        <ol class="breadcrumb mb-4">
                            <li class="breadcrumb-item active">Pilih Tombol, Apabila ingin Melihat Data Lebih Jelas</li>
                        </ol>
                        <!-- Tombol -->
                        <div class="row">
                            <div class="col-xl-2 col-md-6">
                                <div class="card bg-primary text-white mb-4">
                                    <div class="card-body">Matrix</div>
                                    <div class="card-footer d-flex align-items-center justify-content-between">
                                        <form method="post">
                                            <button type="submit" class="small text-white stretched-link" name="matrix" style="background: none; border: none; padding: 0; font-size: 1em;">View Details</button>
                                        </form>
                                        <div class="small text-white"><i class="fas fa-angle-right"></i></div>
                                    </div>
                                </div>
                            </div>
                            <div class="col-xl-2 col-md-6">
                                <div class="card bg-primary text-white mb-4">
                                    <div class="card-body">Normalisasi 1</div>
                                    <div class="card-footer d-flex align-items-center justify-content-between">
                                        <form method="post">
                                            <button type="submit" class="small text-white stretched-link" name="1" style="background: none; border: none; padding: 0; font-size: 1em;">View Details</button>
                                        </form>
                                        <div class="small text-white"><i class="fas fa-angle-right"></i></div>
                                    </div>
                                </div>
                            </div>
                            <div class="col-xl-2 col-md-6">
                                <div class="card bg-primary text-white mb-4">
                                    <div class="card-body">Normalisasi 2</div>
                                    <div class="card-footer d-flex align-items-center justify-content-between">
                                        <form method="post">
                                            <button type="submit" class="small text-white stretched-link" name="2" style="background: none; border: none; padding: 0; font-size: 1em;">View Details</button>
                                        </form>
                                        <div class="small text-white"><i class="fas fa-angle-right"></i></div>
                                    </div>
                                </div>
                            </div>
                            <div class="col-xl-2 col-md-6">
                                <div class="card bg-primary text-white mb-4">
                                    <div class="card-body">Full MultiPlaticative</div>
                                    <div class="card-footer d-flex align-items-center justify-content-between">
                                        <form method="post">
                                            <button type="submit" class="small text-white stretched-link" name="full" style="background: none; border: none; padding: 0; font-size: 1em;">View Details</button>
                                        </form>
                                        <div class="small text-white"><i class="fas fa-angle-right"></i></div>
                                    </div>
                                </div>
                            </div>
                            <div class="col-xl-2 col-md-6">
                                <div class="card bg-primary text-white mb-4">
                                    <div class="card-body">Rasio</div>
                                    <div class="card-footer d-flex align-items-center justify-content-between">
                                        <form method="post">
                                            <button type="submit" class="small text-white stretched-link" name="rasio" style="background: none; border: none; padding: 0; font-size: 1em;">View Details</button>
                                        </form>
                                        <div class="small text-white"><i class="fas fa-angle-right"></i></div>
                                    </div>
                                </div>
                            </div>
                        </div>
                        <!-- if else -->
                        <div class="card mb-4">
                            <div class="card-header">
                                <i class="fas fa-tachometer-alt"></i>
                                <?php echo $judul_tabel; ?>
                            </div>
                            <div class="card-body">
                                <table id="datatablesSimple">
                                    <thead>
                                        <tr>
                                            <!-- Additional header for Matrix -->
                                            <?php if (isset($_POST['matrix'])) : ?>
                                                <th>ID Matrik</th>
                                                <th>ID Alternatif</th>
                                                <th>Nama Alternatif</th>
                                                <th>ID Kriteria</th>
                                                <th>Nama Kriteria</th>
                                                <th>Tipe</th>
                                                <th>ID Bobot</th>
                                                <th>Value</th>
                                                <th>Nilai</th>
                                                <th>Keterangan</th>
                                            <?php endif; ?>
                                            <!-- Additional header for Normalisasi -->
                                            <?php if (isset($_POST['1'])) : ?>
                                                <th>ID Matrik</th>
                                                <th>ID Alternatif</th>
                                                <th>Nama Alternatif</th>
                                                <th>ID Kriteria</th>
                                                <th>Nama Kriteria</th>
                                                <th>Tipe</th>
                                                <th>ID Bobot</th>
                                                <th>Value</th>
                                                <th>Nilai</th>
                                                <th>Keterangan</th>
                                                <th>Pra</th>
                                            <?php endif; ?>
                                            <!-- Additional header for Normalisasi -->
                                            <?php if (isset($_POST['2'])) : ?>
                                                <th>ID Matrik</th>
                                                <th>ID Alternatif</th>
                                                <th>Nama Alternatif</th>
                                                <th>ID Kriteria</th>
                                                <th>Nama Kriteria</th>
                                                <th>Tipe</th>
                                                <th>ID Bobot</th>
                                                <th>Value</th>
                                                <th>Nilai</th>
                                                <th>Keterangan</th>
                                                <th>Pra</th>
                                                <th>Normalisasi</th>
                                            <?php endif; ?>
                                            <?php if (isset($_POST['full'])) : ?>
                                                <th>ID Alternatif</th>
                                                <th>Hasil</th>
                                            <?php endif; ?>
                                            <!-- Additional header for Rangking -->
                                            <?php if (isset($_POST['rasio'])) : ?>
                                                <th>ID Matrik</th>
                                                <th>ID Alternatif</th>
                                                <th>Nama Alternatif</th>
                                                <th>ID Kriteria</th>
                                                <th>Nama Kriteria</th>
                                                <th>Tipe</th>
                                                <th>ID Bobot</th>
                                                <th>Value</th>
                                                <th>Nilai</th>
                                                <th>Keterangan</th>
                                                <th>Pra</th>
                                                <th>Normalisasi</th>
                                                <th>Normalisasi Bobot</th>
                                            <?php endif; ?>
                                        </tr>
                                    </thead>
                                    <tbody>
                                        <?php while ($d = mysqli_fetch_array($data)) : ?>
                                            <!-- Display table rows based on the selected data -->
                                            <tr>
                                                <!-- Display Matrix value if available -->
                                                <?php if (isset($_POST['matrix'])) : ?>
                                                    <th><?php echo $d['id_matrix']; ?></th>
                                                    <th><?php echo $d['id_alternatif']; ?></th>
                                                    <th><?php echo $d['nm_alternatif']; ?></th>
                                                    <th><?php echo $d['id_kriteria']; ?></th>
                                                    <th><?php echo $d['nm_kriteria']; ?></th>
                                                    <th><?php echo $d['tipe']; ?></th>
                                                    <th><?php echo $d['id_bobot']; ?></th>
                                                    <th><?php echo $d['value']; ?></th>
                                                    <th><?php echo $d['nilai']; ?></th>
                                                    <th><?php echo $d['keterangan']; ?></th>
                                                <?php endif; ?>
                                                <!-- Display Normalisasi value if available -->
                                                <?php if (isset($_POST['1'])) : ?>
                                                    <th><?php echo $d['id_matrix']; ?></th>
                                                    <th><?php echo $d['id_alternatif']; ?></th>
                                                    <th><?php echo $d['nm_alternatif']; ?></th>
                                                    <th><?php echo $d['id_kriteria']; ?></th>
                                                    <th><?php echo $d['nm_kriteria']; ?></th>
                                                    <th><?php echo $d['tipe']; ?></th>
                                                    <th><?php echo $d['id_bobot']; ?></th>
                                                    <th><?php echo $d['value']; ?></th>
                                                    <th><?php echo $d['nilai']; ?></th>
                                                    <th><?php echo $d['keterangan']; ?></th>
                                                    <th><?php echo $d['pra']; ?></th>
                                                <?php endif; ?>
                                                <!-- Display Min value if available -->
                                                <?php if (isset($_POST['2'])) : ?>
                                                    <th><?php echo $d['id_matrix']; ?></th>
                                                    <th><?php echo $d['id_alternatif']; ?></th>
                                                    <th><?php echo $d['nm_alternatif']; ?></th>
                                                    <th><?php echo $d['id_kriteria']; ?></th>
                                                    <th><?php echo $d['nm_kriteria']; ?></th>
                                                    <th><?php echo $d['tipe']; ?></th>
                                                    <th><?php echo $d['id_bobot']; ?></th>
                                                    <th><?php echo $d['value']; ?></th>
                                                    <th><?php echo $d['nilai']; ?></th>
                                                    <th><?php echo $d['keterangan']; ?></th>
                                                    <th><?php echo $d['pra']; ?></th>
                                                    <th><?php echo $d['normalisasi']; ?></th>
                                                <?php endif; ?>
                                                <!-- Display Rangking value if available -->
                                                <?php if (isset($_POST['full'])) : ?>
                                                    <th><?php echo $d['id_alternatif']; ?></th>
                                                    <th><?php echo $d['hasil']; ?></th>
                                                <?php endif; ?>
                                                <!-- Display Prarangking value if available -->
                                                <?php if (isset($_POST['rasio'])) : ?>
                                                    <th><?php echo $d['id_matrix']; ?></th>
                                                    <th><?php echo $d['id_alternatif']; ?></th>
                                                    <th><?php echo $d['nm_alternatif']; ?></th>
                                                    <th><?php echo $d['id_kriteria']; ?></th>
                                                    <th><?php echo $d['nm_kriteria']; ?></th>
                                                    <th><?php echo $d['tipe']; ?></th>
                                                    <th><?php echo $d['id_bobot']; ?></th>
                                                    <th><?php echo $d['value']; ?></th>
                                                    <th><?php echo $d['nilai']; ?></th>
                                                    <th><?php echo $d['keterangan']; ?></th>
                                                    <th><?php echo $d['pra']; ?></th>
                                                    <th><?php echo $d['normalisasi']; ?></th>
                                                    <th><?php echo $d['normalisasibobot']; ?></th>
                                                <?php endif; ?>
                                            </tr>
                                        <?php endwhile; ?>
                                    </tbody>
                                </table>
                            </div>
                        </div>
                    </div>
                </main>
                <footer class="py-4 bg-light mt-auto">
                    <div class="container-fluid px-4">
                        <div class="d-flex align-items-center justify-content-between small">
                            <div class="text-muted">Copyright &copy; <i>Iamam Tobroni</i></div>
                        </div>
                    </div>
                </footer>
            </div>
        </div>
        <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.2.3/dist/js/bootstrap.bundle.min.js" crossorigin="anonymous"></script>
        <script src="js/scripts.js"></script>
        <script src="https://cdnjs.cloudflare.com/ajax/libs/Chart.js/2.8.0/Chart.min.js" crossorigin="anonymous"></script>
        <script src="assets/demo/chart-area-demo.js"></script>
        <script src="assets/demo/chart-bar-demo.js"></script>
        <script src="https://cdn.jsdelivr.net/npm/simple-datatables@7.1.2/dist/umd/simple-datatables.min.js" crossorigin="anonymous"></script>
        <script src="js/datatables-simple-demo.js"></script>
    </body>
</html>
