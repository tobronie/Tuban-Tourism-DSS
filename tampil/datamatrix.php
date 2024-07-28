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
    <link href="../css/styles.css" rel="stylesheet" />
    <script src="https://use.fontawesome.com/releases/v6.3.0/js/all.js" crossorigin="anonymous"></script>
</head>

<body class="sb-nav-fixed">
    <nav class="sb-topnav navbar navbar-expand navbar-dark bg-dark">
        <!-- Navbar Brand-->
        <a class="navbar-brand ps-3" href="index.php">Data Wisata</a>
        <!-- Sidebar Toggle-->
        <button class="btn btn-link btn-sm order-1 order-lg-0 me-4 me-lg-0" id="sidebarToggle" href="#!"><i
                class="fas fa-bars"></i></button>
        <!-- Navbar Search-->
        <form class="d-none d-md-inline-block form-inline ms-auto me-0 me-md-3 my-2 my-md-0">
            <div class="input-group">
                <input class="form-control" type="text" placeholder="Search for..." aria-label="Search for..."
                    aria-describedby="btnNavbarSearch" />
                <button class="btn btn-primary" id="btnNavbarSearch" type="button"><i
                        class="fas fa-search"></i></button>
            </div>
        </form>
        <!-- Navbar-->
        <ul class="navbar-nav ms-auto ms-md-0 me-3 me-lg-4">
            <li class="nav-item dropdown">
                <a class="nav-link dropdown-toggle" id="navbarDropdown" href="#" role="button" data-bs-toggle="dropdown"
                    aria-expanded="false"><i class="fas fa-user fa-fw"></i></a>
                <ul class="dropdown-menu dropdown-menu-end" aria-labelledby="navbarDropdown">
                    <li><a class="dropdown-item" href="#!">Settings</a></li>
                    <li><a class="dropdown-item" href="#!">Activity Log</a></li>
                    <li>
                        <hr class="dropdown-divider" />
                    </li>
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
                        <a class="nav-link" href="../index.php">
                            <div class="sb-nav-link-icon"><i class="fas fa-tachometer-alt"></i></div>
                            Dashboard
                        </a>
                        <a class="nav-link collapsed" href="#" data-bs-toggle="collapse"
                            data-bs-target="#collapseLayouts" aria-expanded="false" aria-controls="collapseLayouts">
                            <div class="sb-nav-link-icon"><i class="fas fa-columns"></i></div>
                            Metode
                            <div class="sb-sidenav-collapse-arrow"><i class="fas fa-angle-down"></i></div>
                        </a>
                        <div class="collapse" id="collapseLayouts" aria-labelledby="headingOne"
                            data-bs-parent="#sidenavAccordion">
                            <nav class="sb-sidenav-menu-nested nav">
                                <a class="nav-link" href="../result_saw.php">SAW</a>
                                <a class="nav-link" href="../result_wp.php">WP</a>
                                <a class="nav-link" href="../result_topsis.php">Topsis</a>
                                <a class="nav-link" href="../result_multimoora.php">Multimoora</a>
                            </nav>
                        </div>
                        <a class="nav-link collapsed" href="#" data-bs-toggle="collapse"
                            data-bs-target="#collapseLayoutss" aria-expanded="false" aria-controls="collapseLayouts">
                            <div class="sb-nav-link-icon"><i class="fas fa-columns"></i></div>
                            Tampilan Data
                            <div class="sb-sidenav-collapse-arrow"><i class="fas fa-angle-down"></i></div>
                        </a>
                        <div class="collapse" id="collapseLayoutss" aria-labelledby="headingOne"
                            data-bs-parent="#sidenavAccordion">
                            <nav class="sb-sidenav-menu-nested nav">
                                <a class="nav-link" href="dataalternatif.php">Data Alternatif</a>
                                <a class="nav-link" href="datakriteria.php">Data Kriteria</a>
                                <a class="nav-link" href="databobot.php">Data Bobot</a>
                                <a class="nav-link" href="dataskala.php">Data Skala</a>
                                <a class="nav-link" href="datamatrix.php">Data Matrix</a>
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
                    <h1 class="mt-4">Data Matrix Keputusan</h1>
                    <ol class="breadcrumb mb-4">
                        <li class="breadcrumb-item active">Wisata Pilihan</li>
                    </ol>
                    <div class="card mb-4">
                        <div class="card-header">
                            <i class="fas fa-tachometer-alt"></i>
                            Input Data Matrix Keputusan
                        </div>
                        <div class="card-body">
                            <form method="POST" action="../aksi/insertmatrix.php">
                                <div id="multi-insert-container">
                                    <div class="row mb-3">
                                        <div class="col-md-12 mb-3">
                                            <label for="exampleInputID_A" class="form-label">Nama Alternatif</label>
                                            <select name="id_alternatif[]" id="nm_alternatif" class="form-select"
                                                required>
                                                <?php
                                                include '../config.php';
                                                $result1 = mysqli_query($config, "SELECT id_alternatif, nm_alternatif FROM alternatif
                            WHERE id_alternatif NOT IN (SELECT id_alternatif FROM matrix_keputusan)");

                                                while ($row = $result1->fetch_assoc()) {
                                                    echo '<option value="' . $row['id_alternatif'] . '">' . $row['nm_alternatif'] . '</option>';
                                                }
                                                $result1->free_result();
                                                ?>
                                            </select>
                                        </div>
                                        <?php
                                        $result2 = mysqli_query($config, "SELECT id_kriteria, nm_kriteria FROM kriteria");
                                        while ($row2 = $result2->fetch_assoc()) {
                                            ?>
                                            <div class="col-md-6 kriteriaContainer" style="display: none;">
                                                <label for="exampleInputID_B" class="form-label">Nama Kriteria</label>
                                                <select name="id_bobot[]" class="form-select" required>
                                                    <option value="<?php echo $row2['id_kriteria']; ?>">
                                                        <?php echo $row2['nm_kriteria']; ?>
                                                    </option>
                                                </select>
                                            </div>
                                            <div class="col-md-6 keteranganContainer" style="display: none;">
                                                <label for="exampleInputID_S" class="form-label">Keterangan</label>
                                                <select name="id_skala[]" class="form-select" required>
                                                    <?php
                                                    $result3 = mysqli_query($config, "SELECT id_skala, keterangan FROM skala");
                                                    while ($row3 = $result3->fetch_assoc()) {
                                                        echo '<option value="' . $row3['id_skala'] . '">' . $row3['keterangan'] . '</option>';
                                                    }
                                                    $result3->free_result();
                                                    ?>
                                                </select>
                                            </div>
                                            <?php
                                        }
                                        $result2->free_result();
                                        ?>
                                    </div>
                                </div>
                                <button type="submit" class="btn btn-success">Kirim Data</button>
                            </form>
                            <script>
                                window.onload = function () {
                                    toggleFields();
                                    document.getElementById('nm_alternatif').addEventListener('change', toggleFields);
                                };
                                function toggleFields() {
                                    var nmAlternatif = document.getElementById('nm_alternatif');
                                    var kriteriaContainers = document.querySelectorAll('.kriteriaContainer');
                                    var keteranganContainers = document.querySelectorAll('.keteranganContainer');
                                    if (nmAlternatif.value !== "") {
                                        kriteriaContainers.forEach(function (container) {
                                            container.style.display = 'block';
                                        });
                                        keteranganContainers.forEach(function (container) {
                                            container.style.display = 'block';
                                        });
                                    } else {
                                        kriteriaContainers.forEach(function (container) {
                                            container.style.display = 'none';
                                        });
                                        keteranganContainers.forEach(function (container) {
                                            container.style.display = 'none';
                                        });
                                    }
                                }
                            </script>
                        </div>
                    </div>
                    <div class="card mb-4">
                        <div class="card-header">
                            <i class="fas fa-tachometer-alt"></i>
                            Tabel Data Wisata
                        </div>
                        <div class="card-body">
                            <table id="datatablesSimple">
                                <thead>
                                    <tr>
                                        <th>ID Matrix</th>
                                        <th>Nama Alternatif</th>
                                        <th>Nama Kriteria</th>
                                        <th>Keterangan</th>
                                        <th>Opsi</th>
                                    </tr>
                                </thead>
                                <tfoot>
                                    <tr>
                                        <th>ID Matrix</th>
                                        <th>Nama Alternatif</th>
                                        <th>Nama Kriteria</th>
                                        <th>Keterangan</th>
                                        <th>Opsi</th>
                                    </tr>
                                    <tbody>
                                        <?php
                                        include '../config.php';
                                        $i = 1;
                                        $data = mysqli_query($config, "SELECT alternatif.nm_alternatif, matrix_keputusan.id_matrix, kriteria.nm_kriteria, skala.keterangan
                                        FROM matrix_keputusan
                                        JOIN alternatif ON matrix_keputusan.id_alternatif = alternatif.id_alternatif
                                        JOIN bobot ON matrix_keputusan.id_bobot = bobot.id_bobot
                                        JOIN kriteria ON bobot.id_kriteria = kriteria.id_kriteria
                                        JOIN skala ON matrix_keputusan.id_skala = skala.id_skala
                                        ORDER BY matrix_keputusan.id_matrix");
                                        while ($d = mysqli_fetch_array($data)) {
                                            ?>
                                            <tr>
                                                <th>
                                                    <?php echo $d['id_matrix']; ?>
                                                </th>
                                                <th>
                                                    <?php echo $d['nm_alternatif']; ?>
                                                </th>
                                                <th>
                                                    <?php echo $d['nm_kriteria']; ?>
                                                </th>
                                                <th>
                                                    <?php echo $d['keterangan']; ?>
                                                </th>
                                                <th>
                                                    <a href="../delete/deletematrix.php?id_matrix=<?= $d['id_matrix']; ?>"
                                                        class="btn btn-danger">Delete</a>
                                                </th>
                                            </tr>
                                            <?php
                                        }
                                        ?>
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
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.2.3/dist/js/bootstrap.bundle.min.js"
        crossorigin="anonymous"></script>
    <script src="../js/scripts.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/Chart.js/2.8.0/Chart.min.js" crossorigin="anonymous"></script>
    <script src="../assets/demo/chart-area-demo.js"></script>
    <script src="../assets/demo/chart-bar-demo.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/simple-datatables@7.1.2/dist/umd/simple-datatables.min.js"
        crossorigin="anonymous"></script>
    <script src="../js/datatables-simple-demo.js"></script>
</body>

</html>