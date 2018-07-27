<html>
	<body>
		<?php
			$myPDO = new PDO('sqlite:i2p_database.db');
			if ($myPDO->connect_error) {
				die("Connection failed: " . $myPDO->connect_error);
			} 
			$result = $myPDO->query("SELECT id, name, outgoing_sites, incoming_sites, degree FROM Nodes");
			$total_sites = 0;
			$degree_1_sites = 0;
			$degree_2_sites = 0;
			$degree_3_sites = 0;
			$degree_4_sites = 0;
			$degree_5_sites = 0;
			$degree_6_sites = 0;
			$degree_7_sites = 0;
			$degree_8_sites = 0;
			if ($result->num_rows >= 0) {
				foreach($result as $row)
				{
					$total_sites += 1;
					if ($row['degree'] == 1) { $degree_1_sites +=1; }
					elseif ($row['degree'] == 2) { $degree_2_sites +=1; }
					elseif ($row['degree'] == 3) { $degree_3_sites +=1; }
					elseif ($row['degree'] == 4) { $degree_4_sites +=1; }
					elseif ($row['degree'] == 5) { $degree_5_sites +=1; }
					elseif ($row['degree'] == 6) { $degree_6_sites +=1; }
					elseif ($row['degree'] == 7) { $degree_7_sites +=1; }
					elseif ($row['degree'] == 8) { $degree_8_sites +=1; }
				}
				echo "<table>";
				echo "<tr>";
				echo "  <th> TOTAL sites: </th>";
				echo "  <th> $total_sites </th>";
				echo "</tr>";
				echo "<tr>";
				echo "  <th> Degree 1 sites: </th>";
				echo "  <th> $degree_1_sites </th>";
				echo "</tr>";
				echo "<tr>";
				echo "  <th> Degree 2 sites: </th>";
				echo "  <th> $degree_2_sites </th>";
				echo "</tr>";
				echo "<tr>";
				echo "  <th> Degree 3 sites: </th>";
				echo "  <th> $degree_3_sites </th>";
				echo "</tr>";
				echo "<tr>";
				echo "  <th> Degree 4 sites: </th>";
				echo "  <th> $degree_4_sites </th>";
				echo "</tr>";
				echo "<tr>";
				echo "  <th> Degree 5 sites: </th>";
				echo "  <th> $degree_5_sites </th>";
				echo "</tr>";
				echo "<tr>";
				echo "  <th> Degree 6 sites: </th>";
				echo "  <th> $degree_6_sites </th>";
				echo "</tr>";
				echo "<tr>";
				echo "  <th> Degree 7 sites: </th>";
				echo "  <th> $degree_7_sites </th>";
				echo "</tr>";
				echo "<tr>";
				echo "  <th> Degree 8 sites: </th>";
				echo "  <th> $degree_8_sites </th>";
				echo "</tr>";
				echo "</table>";
			}
			else {
				echo "The query does not return anything";
			}
		?>
	</body>
</html>