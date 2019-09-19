/*
 * Copyright 2019 Kevin J. Burns, P.E.
 * Contact: kevin.burns.pe at gmail dot com
 * This file is part of Traffic Simulation.
 * 
 * Traffic Simulation is free software: you can redistribute it and/or modify 
 * it under the terms of the GNU Lesser General Public License as published by
 * the Free Software Foundation, either version 3 of the License, or
 * (at your option) any later version.
 * 
 * Traffic Simulation is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU Lesser General Public License for more details.
 * 
 * You should have received a copy of the GNU Lesser General Public License
 * along with Traffic Simulation.  If not, see <https://www.gnu.org/licenses/>.
 */
package com.github.kjburns.traffic_simulation.parameters;

import java.util.Iterator;
import java.util.stream.Stream;

public interface VehicleModel extends DistributableThing {
	public interface VehicleUnit {
		boolean hasTrailer();
		Trailer getTrailer_rNull();
		
		String getName();
		/**
		 * Gets the width of the unit <u>in metres</u>.
		 * @return
		 */
		double getWidth();
		/**
		 * Gets the length of the unit <u>in metres</u>.
		 * @return
		 */
		double getLength();
		/**
		 * Gets the distance, <u>in metres</u>, from the front of the 
		 * vehicle to the ball that holds the trailer.
		 * @return
		 */
		double getArticulationDistanceFromFront();
	}
	
	public interface Trailer extends VehicleUnit {
		/**
		 * Gets the distance, <u>in metres</u>, from the front of the 
		 * vehicle to the tongue of the trailer.
		 * @return
		 */
		double getTowingDistanceFromFront();
	}
	
	VehicleUnit getLeadVehicle();
	/**
	 * Gets the total length of the vehicle model <u>in metres</u>.
	 * @return
	 */
	double getTotalLength();
	/**
	 * Gets the maximum width of any vehicle in the combination <u>in metres</u>.
	 * @return
	 */
	double getMaximumWidth();
	String getName();
	/**
	 * Gets the distance <u>in metres</u> from the front of the specified 
	 * unit to the front of the lead vehicle.
	 * @param unit
	 * @return
	 */
	double getDistanceFromFront(VehicleUnit unit);
	Stream<VehicleUnit> unitsStream();
	Iterator<VehicleUnit> unitsIterator();
}
