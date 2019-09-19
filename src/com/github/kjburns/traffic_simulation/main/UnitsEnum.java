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
package com.github.kjburns.traffic_simulation.main;

public enum UnitsEnum {
	METERS(1.0),
	METRES(1.0),
	FEET(0.3048);
	
	private final double factor;
	private UnitsEnum(double _factor) {
		factor = _factor;
	}
	
	public double toThisUnit(double distanceInMetres) {
		return distanceInMetres / factor;
	}
	
	public final double toMetres(double distanceInThisUnit) {
		return distanceInThisUnit * factor;
	}
}
