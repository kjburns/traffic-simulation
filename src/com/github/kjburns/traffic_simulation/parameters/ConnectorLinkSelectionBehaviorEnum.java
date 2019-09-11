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

public enum ConnectorLinkSelectionBehaviorEnum {
	/**
	 * The driver selects the link that results in being in the nearest lane. This is usually the legal option.
	 */
	NEAREST,
	/**
	 * The driver selects the link that results in being in the farthest lane. This is the fastest option.
	 */
	FARTHEST,
	/**
	 * The driver selects the link that results in the fewest required lane changes for the next turn in the route.
	 */
	BEST,
	/**
	 * The driver selects a random link.
	 */
	RANDOM;
}
