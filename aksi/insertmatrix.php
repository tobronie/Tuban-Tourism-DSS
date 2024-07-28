<?php
session_start();
include '../config.php';

if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    if (isset($_POST['id_alternatif']) && isset($_POST['id_bobot']) && isset($_POST['id_skala'])) {
        $id_alternatif_array = $_POST['id_alternatif'];
        $id_bobot_array = $_POST['id_bobot'];
        $id_skala_array = $_POST['id_skala'];
        $insertStmt = mysqli_prepare($config, "INSERT INTO matrix_keputusan (id_alternatif, id_bobot, id_skala) VALUES (?, ?, ?)");
        if ($insertStmt) {
            mysqli_stmt_bind_param($insertStmt, "sss", $ID_A, $ID_B, $ID_S);
            foreach ($id_alternatif_array as $id_alternatif) {
                for ($i = 0; $i < count($id_bobot_array); $i++) {
                    $ID_A = $id_alternatif;
                    $ID_B = $id_bobot_array[$i];
                    $ID_S = $id_skala_array[$i];
                    $checkQuery = "SELECT id_matrix FROM matrix_keputusan WHERE id_alternatif = '$ID_A' AND id_bobot = '$ID_B'";
                    $checkResult = mysqli_query($config, $checkQuery);
                    if (mysqli_num_rows($checkResult) > 0) {
                        echo "Data dengan id_alternatif " . $ID_A . " dan id_bobot " . $ID_B . " sudah ada dalam database.";
                        exit();
                    }
                    mysqli_stmt_execute($insertStmt);
                    echo "Data berhasil disimpan.";
                }
            }
            mysqli_stmt_close($insertStmt);
            header("Location: ../tampil/datamatrix.php");
            exit();
        } else {
            echo "Gagal membuat prepared statement: " . mysqli_error($config);
            exit();
        }
    } else {
        echo "Data yang dibutuhkan tidak lengkap.";
    }
} else {
    echo "Akses ke halaman ini tidak diizinkan.";
}
mysqli_close($config);
?>
