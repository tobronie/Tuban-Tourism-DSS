<?php
include '../config.php';

if ($_SERVER["REQUEST_METHOD"] == "POST") {
    if (!empty($_POST['value']) && !empty($_POST['keterangan'])) {
        $values = $_POST['value'];
        $keterangans = $_POST['keterangan'];
        $count = count($values);
        for ($i = 0; $i < $count; $i++) {
            $value = mysqli_real_escape_string($config, $values[$i]);
            $keterangan = mysqli_real_escape_string($config, $keterangans[$i]);
            $query = "INSERT INTO skala (value, keterangan) VALUES ('$value', '$keterangan')";
            if (!mysqli_query($config, $query)) {
                echo "Error: " . mysqli_error($config);
                exit();
            }
        }
        header("location: ../tampil/dataskala.php");
        exit();
    } else {
        echo "Error: Form data is incomplete.";
    }
} else {
    echo "Form not submitted!";
}
?>